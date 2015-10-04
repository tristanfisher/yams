from flask import Blueprint, jsonify
from ...errors import ValidationError, bad_request, not_found, unauthorized
from yams_api.api import api
from yams_api.utils.logger import log
# resist the urge to do the glob + load approach from plugins

core_bp = Blueprint("core", __name__)


@core_bp.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@core_bp.errorhandler(400)
def bad_request_error(e):
    return bad_request("invalid request")


@core_bp.errorhandler(401)
def unauthorized_error(e):
    return unauthorized_error("permission denied")


@core_bp.errorhandler(404)
def not_found_error(e):
    return not_found("item not found")


core_endpoints = []
def core_set_endpoints():
    if not core_endpoints:
        for api_endpoint in api.url_map.iter_rules():
            if api_endpoint.rule.startswith("/" + core_bp.name):
                url = api_endpoint.rule
                methods = api_endpoint.methods
                core_endpoints.append((url, str(methods)))
            core_endpoints.sort()
    else:
        return core_endpoints


@core_bp.route("/")
def core_index():
    return jsonify(core_endpoints)
