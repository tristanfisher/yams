from flask import jsonify, g
import boto
import boto.ec2
from boto.ec2 import connect_to_region
from boto.exception import NoAuthHandlerFound
import yams_api.api
import requests
import json
import re
from yams_api.utils.logger import log

from boto import connect_ec2, connect_s3, connect_vpc
from lxml.html import fromstring as html_string

from config import ThirdParty

ACCESS_KEY = ThirdParty.AWS_ACCESS_KEY_ID
SECRET_KEY = ThirdParty.AWS_SECRET_ACCESS_KEY


class AWSResource:

    def __init__(self, resource=None, region=None, filter=None, attribute=None):

        self.resource = resource
        if not region:
            region = 'us-east-1'
        self.region = region
        self.match_all_param = ['*', '%', 'all']
        self.filter = filter
        self.attribute = attribute
        self.conn_methods = {
            "ec2": connect_to_region,
            "s3": connect_s3,
            "vpc": connect_vpc
        }
        # our own little traceback stack. how cute.
        self.errors = []


    def __repr__(self):
        return "<AWSResource: '{}'>".format(self.resource)

    #http://boto.readthedocs.org/en/latest/ref/ec2.html
    def get_resource(self, tag_filters={}, attrib=""):

        conn = self.conn_methods["ec2"](region_name=self.region)

        # add logic flow when we need to look up more than instances
        # gets reservations: instance.__dict__ for _instance in conn.get_all_instances(filters=tag_filters)]
        conn = conn.get_only_instances(filters={"instance_id": self.resource})

        #todo: all attrs by default and allow filtering as a class attribute
        response  = ["%s : %s" % (i.tags["Name"], i.dns_name) for i in conn]

        # instance_list.append({"count": len(instance_list)})
        # can be json
        return response

    # ------------------------------------------------------------------------ #
    # maybe refactor these to properties so setter appends, deleter clears to empty list
    def get_error_list(self):
        return self.errors

    def clear_error_list(self):
        self.errors = []

    def response(self):
        return jsonify(ok="not implemented")


# http://boto.readthedocs.org/en/latest/boto_config_tut.html  if permission denied, set this.
class AWSPrivateResource(AWSResource):

    def __init__(self, resource=None, ec2_connection=None, access_key=ACCESS_KEY, secret_key=SECRET_KEY):
        self.resource = resource
        self._ec2_connection = ec2_connection
        super().__init__(resource=resource)

        self.resource_regional_connection_method_table = {
            "ec2": boto.ec2.connect_to_region
        }

        self.resource_connection_method_table = {
            "s3": boto.connect_s3,
            "vpc": boto.connect_vpc
        }

        # structure is:
        # for regional connections      => [resource][region]:connection
        self.aws_connections = dict()
        for _regional_resource in self.resource_regional_connection_method_table:
            self.aws_connections[_regional_resource] = {}
            # unneeded, but here's why we built this structure:
            self.aws_connections[_regional_resource][self.region] = None

        # for non-regional connections  => [resource]:connection
        for _resource in self.resource_connection_method_table:
            self.aws_connections[_resource] = None

        self.access_key = access_key
        self.secret_key = secret_key
        self.credentials_are_set = bool(self.access_key) and bool(self.secret_key)


    # ------------------------------------------------------------------------ #
    # Connection get/set
    # -- this could all deal with more exception handling --

    @property
    def ec2_connection(self, region=None):

        # return the default region connection for the object
        if not region:
            region = self.region

        _ = self.aws_connections['ec2'].get(region)
        if not _:
            if self.set_ec2_connection(resource="ec2", region=region):
                _ = self.aws_connections['ec2'][region]

        return _

    def get_ec2_connection(self, resource="ec2", region=None):

        if not region:
            region = self.region

        if resource in self.resource_regional_connection_method_table:
            _ = self.aws_connections.get(region, None)

            if not _:
                if self.set_ec2_connection(resource=resource, region=region):
                    _res = self.aws_connections.get(resource, None)
                    if _res:
                        _ = _res.get(region, None)
            return _
        else:
            _ = self.aws_connections[resource].get(region, None)
            if not _:
                if self.set_ec2_connection(resource=resource, region=region):
                    _ = self.aws_connections[resource].get(region, None)
            return _

    # no point in making this a normal property setter, it will usually be called without params
    def set_ec2_connection(self, resource="ec2", ec2_conn=None, region=None, access_key=None, secret_key=None):
        # if we were handed a connection object and a region, bind it.
        if ec2_conn and region:
            self.aws_connections[region] = ec2_conn

        if not region:
            region = self.region

        if not (access_key and secret_key):
            if self.credentials_are_set:
                access_key = self.access_key
                secret_key = self.secret_key

        if bool(access_key) and bool(secret_key):

            if resource in self.resource_regional_connection_method_table:
                _conn_method = self.resource_regional_connection_method_table[resource]
                self.aws_connections[resource][region] = _conn_method(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            else:
                try:
                    _conn_method = self.resource_connection_method_table[resource]
                    self.aws_connections[resource] = _conn_method(aws_access_key_id=access_key, aws_secret_access_key=secret_key)

                except KeyError:
                    msg = "Unknown connection method for %s.  Check your typing and/or issue a feature request." % resource
                    log.error(msg)
                    self.errors.append(msg)

            return True

        else:
            msg = "Could not create a connection to EC2.  Missing access/secret key or both."
            log.error(msg)
            self.errors.append(msg)
            return False

    # ------------------------------------------------------------------------ #

    def get_all_instance_status_objects(self, region=None):

        _result = []

        if not region:
            region = self.region

        _conn = self.get_ec2_connection(region=self.region)

        if _conn:
            _result = _conn.get_all_instance_status()
        if _result:
            return _result
        else:
            msg = "failed to get instance status"
            log.error(msg)
            self.errors.append(msg)
            return False

    def get_all_instance_notifications(self, region=None, denote_completed=True, show_completed=True):

        if not region:
            region = self.region

        _iso = self.get_all_instance_status_objects(region=region)

        if not _iso:
            _ = self.get_error_list()
            self.clear_error_list()
            return _

        instances_pending_events = dict()
        for _instance_obj in _iso:
            if _instance_obj.events:

                instances_pending_events[_instance_obj.id] = dict()
                _ins_entry = instances_pending_events[_instance_obj.id]

                _ins_entry['zone'] = _instance_obj.zone

                _stat = str(_instance_obj.instance_status).split("Status:")
                if _stat[1]:
                    _stat = _stat[1]
                else:
                    _stat = str(_instance_obj.instance_status)

                _ins_entry['instance_status'] = _stat
                _ins_entry['state_code'] = _instance_obj.state_code
                _ins_entry['state_name'] = _instance_obj.state_name

                _ins_entry['events'] = []

                for _ins_event in _instance_obj.events:

                    _ev = {}

                    _ev['code'] = _ins_event.code
                    _ev['description'] = _ins_event.description
                    _ev['not_before'] = _ins_event.not_before
                    _ev['not_after'] = _ins_event.not_after

                    # parse event description for completed text
                    bool_completed = bool(re.match('^\[Completed\]', _ins_event.description))

                    _ev['completed'] = bool_completed
                    if denote_completed:
                        _ev['not_before'] = "Complete"
                        _ev['not_after'] = "Complete"


                    # todo: a timedelta on the completed time to support a "give me future events and last 48 hours"
                    # if the event is completed and we've been told not to show completed, continue the iter, skipping
                    # the append step
                    if bool_completed and (not show_completed):
                        continue

                    _ins_entry['events'].append(_ev)

        # grab the ids from the list of the interesting hosts (instance ids are the dict keys)
        _instance_ids = [ _id for _id in instances_pending_events]

        # Build an attribute lookup table - do 1 call instead of N; grabbing details only on hosts we're interested in.
        # [Instance:i-123456ab, Instance:i.....]
        _instance_details = self.get_ec2_connection(region=region).get_only_instances(filters={"instance_id": _instance_ids})

        for _i_obj in _instance_details:
            # Unless something went really wrong, the instance tags we have should line up.
            instances_pending_events[_i_obj.id]['tags'] = _i_obj.tags

        from pprint import pprint
        pprint(instances_pending_events)

        return instances_pending_events


class AWSPublicResource:
    """Resources that don't require authentication or credentials (e.g. public status)"""

    def __init__(self):

        self.current_status_ok = "Service is operating normally"
        self.current_status_warning = "Informational message"
        self.current_status_error = "Performance issues"
        self.current_status_outage = "Service disruption"
        self.regions = 'all'
        self.follow_rss = False

        self.aws_current_status_lookup = {
            self.current_status_ok: 'ok',
            self.current_status_warning: 'warning',
            self.current_status_error: 'error',
            self.current_status_outage: 'outage'
        }

        self.status_endpoint = "http://status.aws.amazon.com/"

    def get_aws_endpoint_status(self, regions=None):

        # todo: needs a "i only care about service x,y,z"

        if not regions:
            regions = self.regions

        r = requests.get(self.status_endpoint)

        # need to log the following types of errors and handle them
        # try:
        #     r = requests.get(endpoint)
        # except requests.ConnectionError:
        # except requests.Timeout:
        # except requests.HTTPError:
        # except requests.TooManyRedirects:

        rc = r.status_code
        rt = r.text
        rheaders = r.headers

        _resp = {
            "response": {},
            "headers": {}
        }

        _resp["headers"]["status_code"] = rc
        # not the same as date of response
        _resp["headers"]["last-modified"] = rheaders.get("last-modified", "")
        _resp["headers"]["etag"] = rheaders.get("etag", "")

        # todo: convert date to standard format or return "now"
        _resp["headers"]["date"] = rheaders.get("date", "")

        if str(rc).startswith("2"):
            # if we received an OK from Amazon, then continue processing

            if "json" in rheaders["content-type"]:
                # this would be unexpected -- amazon returns text/html for their status page.
                # this suggests we hit some other page
                _resp["response"] = "unexpected content-type"

                # should be a roll-up status -- e.g. if we parse the fields and there aren't outages..
                # otherwise this is pseudo-redundant of the status_code.

            else:
                """
                # parse the html/text body of the response. caution: it's not valid xml.
                //html/body/div
                /div[contains(@class, "gradient")]
                /div[@id="current_events_block"]
                /div[contains(@class, "yui-content")]
                <<children>> <— table with tbody tr that we care about
                """
                _rtxml = html_string(rt)
                _rtxml_regions_divs = _rtxml.xpath('//html/body/div/div[contains(@class, "gradient")]/div[@id="current_events_block"]/div[contains(@class, "yui-content")]')

                # could be more efficient, but good enough (searches through container div each time)
                # -> will give a list of divs _rtxml_regions_divs = _rtxml_regions_divs[0].xpath("div")
                region_NA = _rtxml_regions_divs[0].xpath("div[contains(@id, 'NA_block')]/table/tbody")[0]
                region_SA = _rtxml_regions_divs[0].xpath("div[contains(@id, 'SA_block')]/table/tbody")[0]
                region_EU = _rtxml_regions_divs[0].xpath("div[contains(@id, 'EU_block')]/table/tbody")[0]
                region_AP = _rtxml_regions_divs[0].xpath("div[contains(@id, 'AP_block')]/table/tbody")[0]

                region_table = {
                    'us': region_NA,
                    'sa': region_SA,
                    'eu': region_EU,
                    'ap': region_AP
                }
                lookup_regions = []

                # At this point, we will only want to parse tables and make calls for the region the user requested
                if regions in ['all', '*'] or regions == ['*']:
                    lookup_regions = ['us', 'sa', 'eu', 'ap']
                    #lookup_regions = [region_table['us'], region_table['sa'], region_table['eu'], region_table['ap']]
                #else:
                #    for region in regions:
                #        lookup_regions.append(region_table[region])

                _response_dict = {}
                for r in lookup_regions:

                    service_rows = region_table[r].getchildren()

                    for row in service_rows:

                        # get the tds
                        _r = row.getchildren()

                        # we're spot checking. parse the text instead of doing N calls to the RSS feeds.
                        # useful if we drop into a database anyway with timestamp

                        # [0] is status icon

                        # the instance status can be strange if the status is "[RESOLVED] issue":
                        # <td class="bb pad8">
                        #     <div class="floatLeft">[RESOLVED] Instance Connectivity </div>
                        #     &nbsp;&nbsp;&nbsp;&nbsp;<a href="#" onclick="toggleCurrent(this, 'current_ec2-us-east-1_1452813122_NA');return(false);">more&nbsp;<img src="/images/more.gif"></a>
                        #     <div class="clear"></div>
                        #     <div id="current_ec2-us-east-1_1452813122_NA" style="display: none; margin-top: 8px;" class="yellowbg bordered-dark pad8">
                        #     <div><span class="yellowfg"> 3:13 PM PST</span>&nbsp;We are investigating connectivity issues for some instances in the US-EAST-1 Region.</div><div><span class="yellowfg"> 3:33 PM PST</span>&nbsp;We can confirm connectivity issues when using public IP addresses for some instances within the EC2-Classic network in the US-EAST-1 Region. Connectivity between instances when using private IP addresses is not affected. We continue to work on resolution.</div><div><span class="yellowfg"> 4:00 PM PST</span>&nbsp;We continue to work on resolving the connectivity issues when using public IP addresses for some instances within the EC2-Classic network in the US-EAST-1 Region. For instances with an associated Elastic IP address (EIP), we have confirmed that re-associating the EIP address will restore connectivity. For instances using EC2 provided public IP addresses, associating a new EIP address will restore connectivity.</div><div><span class="yellowfg"> 6:19 PM PST</span>&nbsp; We continue to work on resolving public IP address connectivity for some EC2-Classic instances in the US-EAST-1 Region. We have started to see recovery for some of the affected instances and continue to work towards full recovery.</div><div><span class="yellowfg"> 7:11 PM PST</span>&nbsp;Between 2:26 PM and 7:10 PM PST we experienced connectivity issues when using public IP addresses for some instances within the EC2 Classic network in the US-EAST-1 Region. Connectivity between instances using the private IP address was not affected. The issue has been resolved and the service is operating normally.</div>
                        #     </div>
                        # </td>

                        try:
                            _status = self.aws_current_status_lookup[_r[2].text]
                        except KeyError:
                            # probably "\n"
                            try:
                                _status = _r[2][0].text
                            except IndexError:
                                _status = "ERROR FETCHING STATUS"

                        _response_dict[_r[1].text] = {
                            'detail': _r[2].text,
                            'rss': _r[3].getchildren()[0].items()[0][1],
                            'status': _status
                        }

                        # in case it's decidedly cleaner to use .update
                        # _ret = {}
                        # _ret['service'] = _r[1].text
                        # _ret['detail'] = _r[2].text
                        # _ret['rss'] = _r[3].getchildren()[0].items()[0][1]
                        # _ret['status'] = self.aws_current_status_lookup[_ret['detail']]

                        if self.follow_rss:
                            pass
                            # todo: async fire off requests to each
                            # this definitely needs async handling.  do not enable without.

                    _resp["response"] = _response_dict
                return _resp
        else:
            # todo: parse var rt for useful info when we know what such an error looks like
            _resp["response"] = rt

        return _resp