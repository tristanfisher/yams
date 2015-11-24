from flask import jsonify, g
import boto
import boto.ec2
from boto.ec2 import connect_to_region
from boto.exception import NoAuthHandlerFound
import yams_api.api
import requests
import json

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

    def response(self):
        return jsonify(ok="not implemented")


# http://boto.readthedocs.org/en/latest/boto_config_tut.html  if permission denied, set this.
class AWSPrivateResource(AWSResource):

    def __init__(self, resource=None, ec2_connection=None, access_key=ACCESS_KEY, secret_key=SECRET_KEY):
        self.resource = resource
        self._ec2_connection = ec2_connection
        super().__init__(resource=resource)

        # boto.connect_ec2()
        self.errors = []

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
        if not region:
            region = self.region

        # return the default region connection for the object
        return self.aws_connections['ec2'][region]

    def get_ec2_connection(self, resource, region_name=None):
        if not region_name:
            region = self.region

        if resource in self.resource_regional_connection_method_table:
            return self.aws_connections[region]
        else:
            return self.aws_connections[resource][region]


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
                    self.errors.append("Unknown connection method for %s.  "
                                       "Check your typing and/or issue a feature request." % resource)

            return True

        else:
            self.errors.append("Could not create a connection to EC2.  Missing access/secret key or both.")
            return False


    # ------------------------------------------------------------------------ #

    def get_all_instance_status(self):
        statuses = self.ec2_connection.get_all_instance_status()
        return statuses


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
        _resp["headers"]["date"] = rheaders.get("last-modified", "")
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
                        _response_dict[_r[1].text] = {
                            'detail': _r[2].text,
                            'rss': _r[3].getchildren()[0].items()[0][1],
                            'status': self.aws_current_status_lookup[_r[2].text]
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


def get_all_instance_status():
    _aws_resource = AWSPrivateResource