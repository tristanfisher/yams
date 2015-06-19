from flask import jsonify, g
import boto
import boto.ec2
from boto.exception import NoAuthHandlerFound
import yams.app

from yams_api.plugins.dev import dev_bp
from werkzeug.local import LocalProxy

from boto import connect_ec2, connect_s3, connect_vpc


class AWSResource:

    def __init__(self, resource=None, region=None, filter=None, attribute=None):

        self.resource = resource
        self.region = region if region else yams.app.config['AWS'].REGION
        self.filter = filter
        self.attribute = attribute
        self.conn_methods = {
            'ec2': connect_ec2,
            's3': connect_s3,
            'vpc': connect_vpc
        }

        self.getter_table = {
            'ec2': self.get_instances(tag_filters=filter, attrib=attribute)
        }


    #http://boto.readthedocs.org/en/latest/ref/ec2.html
    def get_instances(self, tag_filters={}, attrib=""):
        conn = self.conn_methods['ec2'](region=self.region)

        instance_list = [_instance.__dict__ for _instance in conn.get_all_instances(filters=tag_filters)]
        instance_list = [getattr(it, attrib, "") for n in instance_list for it in n["instances"]]
        instance_list.append({"records": len(instance_list)})
        instance_list.append({"status_code": 200})

        return jsonify(response=instance_list)


    def response(self):
        return 'not implemented'

# http://boto.readthedocs.org/en/latest/boto_config_tut.html  if permission denied, set this.
