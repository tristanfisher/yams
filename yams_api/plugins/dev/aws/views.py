from flask import jsonify, request
from yams_api.plugins.dev import dev_bp

from werkzeug.local import LocalProxy

from yams_api.plugins.dev.aws import methods

import boto
from boto.exception import NoAuthHandlerFound




# todo: bind a connection for the proper region.


@dev_bp.route('/aws')
def aws():
    return jsonify(status="ok")

@dev_bp.route('/aws/ec2/<resource>')
def aws_ec2_item(resource):

    # split on the query string/filters
    # request.query_string for all, request.args.get('') for one
    try:
        resp = methods.AWSResource(resource, filter=request.query_string)
        resp = resp.response()
    except:
        # todo: implement a more responsible exception process
        resp = None

    if resp:
        r, code = resp, 200
    else:
        r, code = "error", 500

    return jsonify(response=r), code


@dev_bp.route('/aws/status')
def aws_status():
    return jsonify(status="ok")