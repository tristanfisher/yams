import importlib
import glob
import os
from flask import Blueprint
from flask import g
from flask import jsonify
from ...errors import ValidationError, bad_request, not_found
from yams_api import core
from yams_api.api import api
from yams_api.utils.logger import log

dev_bp = Blueprint("plugins", __name__)
dev_bp.local_object = {}

from importlib.machinery import SourceFileLoader

_here = os.path.abspath(os.path.dirname(__file__))
plugins = glob.glob(_here + "/*/views.py")

for _p in plugins:
    try:
        _plug_dirname = os.path.split(os.path.split(_p)[0])[1]

        # This is ugly: __import__("yams_api.dev.plugins.%s.views" % (_plug_dirname))
        _mod_name = "%s.views" % _plug_dirname
        s = SourceFileLoader(_mod_name, _p).load_module()

    except ImportError as e:
        log.critical("Failed to import module: %s :: %s" % (_p, e))


# error handling and request behavior
@dev_bp.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@dev_bp.errorhandler(400)
def bad_request_error(e):
    return bad_request("invalid request")


@dev_bp.errorhandler(404)
def not_found_error(e):
    return not_found("item not found")


@dev_bp.after_request
def after_request(response):
    if hasattr(g, "headers"):
        response.headers.extend(g.headers)
    return response


# todo: this is a good candidate for being moved to utils
# Look at the url_map for the api, picking out the version specific endpoints,
# then sort them in place.  We do this so we get the prefix from the blueprint.
# This is in a function because the registration on the "api" Flask object
# happens after import.
dev_endpoints = []
def dev_set_endpoints():
    if not dev_endpoints:
        for api_endpoint in api.url_map.iter_rules():
            if api_endpoint.rule.startswith("/" + dev_bp.name):
                url = api_endpoint.rule
                methods = api_endpoint.methods
                dev_endpoints.append((url, str(methods)))
            dev_endpoints.sort()
    else:
        return dev_endpoints


@dev_bp.route("/")
def dev_index():
    return jsonify(dev_endpoints)
