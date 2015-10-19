from flask import jsonify, request
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.aws import methods
from config import DEBUG

# bind a public resource object here so we don't pay every time
public_resource = methods.AWSPublicResource()

# todo: bind a connection for the proper region.
# todo: show documentation on get to /aws or /aws/
@dev_bp.route('/aws/')
def aws():
    return jsonify(status="ok")


@dev_bp.route('/aws/ec2/<resource>')
def aws_ec2_item(resource):

    # todo: split on the query string/filters
    # request.query_string for all, request.args.get('') for one
    try:
        resp = methods.AWSResource(resource, filter=request.query_string)
        resp = resp.get_resource()
        code = 200

    except Exception as e:
        # todo: implement a more responsible exception process
        resp = "error"
        code = 500

        if DEBUG:
            resp = str(e)

    return jsonify(response=resp), code


@dev_bp.route('/aws/ec2/tag/<tag_key>/<tag_value>')
def aws_ec2_quick_tag(tag_key, tag_value):
    # enable a quick lookup like yams:/aws/ec2/tag/environment/development
    pass


@dev_bp.route('/aws/status')
def aws_status():
    # todo: do async call to get status
    _resp = public_resource.get_aws_endpoint_status()

    return jsonify(response=_resp)
