from flask import jsonify, request
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.aws import methods
from config import DEBUG, ThirdParty

# bind a public resource object here so we don't pay every time
public_resource = methods.AWSPublicResource()

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

    except (Exception) as e:
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


@dev_bp.route('/aws/status', defaults={'path': ''})
@dev_bp.route('/aws/status/<path:path>')
def aws_status(path):

    # AWSPrivateResource gets regions and access credentials as needed from config
    private_resource = methods.AWSPrivateResource()

    status_endpoint_function_table = {
        "instance_notifications": private_resource.get_all_instance_notifications
    }

    if not path:
        _resp = public_resource.get_aws_endpoint_status()
        return jsonify(response=_resp)

    _function = status_endpoint_function_table.get(path, None)
    if _function:
        _response = _function()
    else:
        _response = ()

    return jsonify(response=_response)