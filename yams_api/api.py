import os
from flask import Flask, jsonify
from .errors import bad_request, not_found, ValidationError
api = Flask(__name__)
ep = []

from yams_api.dev import dev_bp, dev_set_endpoints
api.register_blueprint(dev_bp, url_prefix="/dev")
dev_set_endpoints()


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.errorhandler(400)
def bad_request_error(e):
    return bad_request("invalid request")


@api.errorhandler(404)
def not_found_error(e):
    return not_found("route not found")


@api.route("/")
def endpoints(url_filter=None):

    # extend this when adding new version
    # this is filtering by name so we can conceal some endpoints
    if not ep:
        for api_endpoint in api.url_map.iter_rules():
            if api_endpoint.rule.startswith("/" + dev_bp.name):
                url = api_endpoint.rule
                methods = api_endpoint.methods
                ep.append((url, str(methods)))

            if api_endpoint.rule == "/status/":
                url = api_endpoint.rule
                methods = api_endpoint.methods
                ep.append((url, str(methods)))

        ep.sort()

    # thinking about doing the following instead:
    # {
    #     "version": {
    #         "v1": {"/version/url/": "--methods--", "/version/url2/": "--methods--" }
    #     }
    # }

    return jsonify(ep)


@api.route("/status/")
def status():
    return jsonify(status="ok")