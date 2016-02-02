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

from sys import exit
import os
from flask import Flask, Blueprint, render_template, g, flash, jsonify, redirect, request, url_for
from flask_login import LoginManager, UserMixin, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from config import SETUP, APP, API, PREFERRED_URL_SCHEME
from yams_api.utils.logger import log
from yams.core.dev.users.methods import User, YAMSAnonymousUser
from json import loads, dumps


API_HOST = "%s://%s:%s" % (PREFERRED_URL_SCHEME, API.LISTEN_HOST, API.LISTEN_PORT)

app = Flask(__name__)
app.config.from_object(os.environ.get("FLASK_CONFIG") or "config")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# this should only be used for db operations related to the web interface.
# if you are associating models with this, you more than likely want the API DB.
app_db = SQLAlchemy(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = YAMSAnonymousUser

@login_manager.user_loader
def load_user():

    # we should be serving static assets from the webserver, but put this in anyway
    # because hammering the DB or k/v store for N-assets is aggressive
    if request.endpoint != 'login' and '/static/' not in request.path:
        print('hooked')
        # use api_key instead and keep user outside of token?
        token = request.headers.get('Authorization')
        if token is None:
            token = request.args.get('token')

        if token is not None:
            # todo: decide on token format
            username, token_hash = token.split(":")
            yams_user = User(username=username, supplied_token=token_hash)

            if yams_user is not None:
                if yams_user.token_valid():
                    return yams_user
                else:
                    # token mismatch
                    flash("Credential error. Please clear your cache or log out and try again.  "
                          "You have been given the permissions of a guest.")

app.before_request(load_user)

navigation_dictionary_list = [
    {"link": "/", "text": "/index", "glyphicon": "glyphicon-home"},
    # use an image that looks like: {...}
    {"link": API_HOST, "text": "browse api", "glyphicon": "glyphicon-console"},
    # search... glyphicon-search
    # {"link": "", "text": "configure page", "glyphicon": "glyphicon-cog"},
    # {"link": "", "text": "save dashboard", "glyphicon": "glyphicon-floppy-disk"},
    # {"link": "", "text": "load dashboard", "glyphicon": "glyphicon-open"}
]

# blueprint routes
from yams.core.dev import core_dev_blueprints
for bp in core_dev_blueprints:

    if bp.url_prefix == '/' or not bp.url_prefix:
        exit("Blueprint %s tried to assert itself as the root path ('/')")

    app.register_blueprint(bp, url_prefix=getattr(bp, 'prefix', None))


def append_to_navigation_menu(dictionary):
    navigation_dictionary_list.append(dictionary)


@app.context_processor
def inject_site_name():
    return dict(site_name=APP.SITE_NAME)


@app.context_processor
def inject_navbar(navigation_dict=navigation_dictionary_list):
    return dict(navbar_items=navigation_dict)

# Load the version of core specified by the user to pin
try:
    __import__("yams_api.core.%s" % APP.API_VERSION_CORE)
except ImportError as e:
    log.critical("Failed to load core version: %s" % e)
    exit(1)

@app.template_filter()
def to_json_valid_or_error(data_dict):
    """Validate JSON, returning an

    :param json_blob: the json data you want to validate
    :return: json_blob unchanged or {"status": "nok"}
    """
    try:
        json_blob = dumps(data_dict)
    except ValueError:
        json_blob = {"status": "nok"}
    return json_blob


@app.template_filter()
def to_bootstrap_size(size):
    """Snap the size to the closest equivalent in bootstrap.

    :param size: size requested by user
    :return: size valid for bootstrap's layout or floor()
    """
    bootstrap_sizes = [1, 3, 4, 6, 12]

    percent_size_mapping = {
        100: 12,
        50: 6,
        30: 4,
        25: 3,
        10: 1,
    }

    if isinstance(size, str):

        size_was_percent = False
        size_original = size

        if "%" in size:
            size = size.replace("%", "")
            size_was_percent = True

        elif "px" in size or "em" in size:
            # don't want to guess view sizes yet, this skips bootstrap size check
            return size

        try:
            # do general float recasting here as it could be any number of failures from above
            # e.g. "%" replaced, but "#" was in the size
            size = float(size)

            if size_was_percent:
                # default to original value if not in percent size mapping
                size = percent_size_mapping.get(int(size), size)

            else:
                # if not using round(), then check absval distance from x->ceiling; x->floor and snap to the closer one
                # this will do 99->100.00, 13->10.0 -- if we did percent size mapping, we'll have a small integer that will
                # round down to nothing
                size = round(size, -1)

        except ValueError:
            return size_original

    # no need to do a bisect solution with how often this is called for such a small comparison list
    size = min(bootstrap_sizes, key=lambda x: abs(x - size))
    return size


@app.route('/status')
def yams_status():

    api = dict()
    databases = dict()
    api["host"] = API_HOST
    databases["name"] = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    return jsonify(
        status="ok",
        api=api,
        databases=databases
    )


@app.route('/whoami')
def yams_whoami():
    # should return information about current user -- id and email should suffice
    return jsonify()


@app.route('/')
def index():

    # todo: also work in a "informational only" type of box -- not everything will be up/down
    # todo: allow user specification of what constitutes up/down/warning
    yams_debug_mode = dumps(APP.DEBUG_FRONTEND)
    yams_api_address = API.LISTEN_URL + "/"
    issue_project_tracker = "https://github.com/tristanfisher/yams/issues"

    # this should pull from yaml/json or a datastore
    user_layout_panels = [
        {
            "id": 1,
            "label": "amazon",
            "boxes": [
                {
                    "id": 1,
                    "label": "api status",
                    "width": "25%",
                    "height": "100%",
                    "data": {
                        "update_method": {
                            "interval_seconds": 30, "type": "polling"
                        },
                        "endpoint": yams_api_address + "plugins/aws/status",
                        # vs series, etc
                        "data_type": "spot",
                        "field": {"response": {"response": "status"}},
                        "field_type": "glob_string",
                        "display_type": "list",
                        "detail_text_field": {'response': 'response'}
                    },
                    "enabled": 1
                }
            ]
        },
        {
            "id": 2,
            "label": "third parties",
            "boxes": [
                {
                    "id": 1,
                    "label": "github status",
                    "width": "25%",
                    "height": "100%",
                    "data": {
                        "update_method": {
                            "interval_seconds": 30, "type": "polling"
                        },
                        "endpoint": yams_api_address + "plugins/github/status",
                        "data_type": "spot",
                        "logic": "boolean",
                        "field": {"response":"status"},
                        "field_type": "string",
                        "display_type": "list",
                        "detail_text_field": {'response': 'response'},
                    },
                    "enabled": 1
                },
                {
                    "id": 2,
                    "label": "dropbox status",
                    "width": "25%",
                    "height": "100%",
                    "data": {
                        "update_method": {
                            "interval_seconds": 30, "type": "polling"
                        },
                        "endpoint": yams_api_address + "plugins/dropbox/status",
                        "data_type": "spot",
                        "logic": "boolean",
                        "field": {"response":"status"},
                        "field_type": "string",
                        "display_type": "list",
                        "detail_text_field": {'response': 'response'},
                    },
                    "enabled": 1
                }
            ]
        }
    ];

    # todo: if we don't have a panel, return help.
    # the panels=object is the target of loading from the user's storage.
    return render_template("index.html",
                            yams_debug_mode=yams_debug_mode,
                            yams_api_address=yams_api_address,
                            issue_project_tracker=issue_project_tracker,
                            user=current_user.username,
                            panels=user_layout_panels
                           )
