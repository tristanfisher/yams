# This file is part of YAMS.
#
# YAMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YAMS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YAMS.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask, jsonify
from config import API
from .errors import bad_request, not_found, ValidationError
from flask.ext.sqlalchemy import SQLAlchemy
import os

api = Flask(__name__)
api.config.from_object(os.environ.get("FLASK_API_CONFIG" or "config"))
db = SQLAlchemy(api)


from yams_api.core.dev import core_bp, core_set_endpoints
from yams_api.plugins.dev import dev_bp, dev_set_endpoints
api.register_blueprint(dev_bp, url_prefix="/plugins")
api.register_blueprint(core_bp, url_prefix="/core")
dev_set_endpoints()
core_set_endpoints()

#
# n.b. the core api is versioned. refrain from adding endpoints
#      in this file.

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.errorhandler(400)
def bad_request_error(e):
    return bad_request("invalid request")


@api.errorhandler(404)
def not_found_error(e):
    return not_found("route not found")


@api.route("/status")
def status():
    return jsonify(status="ok",
                   api_version_core=API.API_VERSION_CORE,
                   api_version_api=API.API_VERSION_PLUGINS)


ep = []
def set_endpoints():
    if not ep:
        for api_endpoint in api.url_map.iter_rules():

            # extend this when adding new version
            # this is filtering by name so we can conceal some endpoints
            if api_endpoint.rule.startswith("/" + dev_bp.name):
                url = api_endpoint.rule
                methods = api_endpoint.methods
                ep.append((url, str(methods)))

            if api_endpoint.rule.startswith("/" + core_bp.name):
                url = api_endpoint.rule
                methods = api_endpoint.methods
                ep.append((url, str(methods)))

            if api_endpoint.rule == "/status/":
                url = api_endpoint.rule
                methods = api_endpoint.methods
                ep.append((url, str(methods)))
        ep.sort()
    else:
        return ep

    # thinking about doing the following instead:
    # {
    #     "version": {
    #         "v1": {"/version/url/": "--methods--", "/version/url2/": "--methods--" }
    #     }
    # }
set_endpoints()


@api.route("/")
def endpoints(url_filter=None):
    return jsonify(ep)