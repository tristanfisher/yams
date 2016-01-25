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
from flask import Flask, Blueprint, render_template, g
from flask import jsonify, redirect, request, url_for
from flask_login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from config import SETUP, APP, API, PREFERRED_URL_SCHEME
from yams_api.utils.logger import log
from collections import namedtuple
from yams.core.dev.users import methods
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

Guest = namedtuple('guest_user', ['id', 'name', 'email', 'is_authenticated', 'active'])

@login_manager.user_loader
def load_user(user_id):

    guest = Guest(0, 'guest', '', True, True)

    if not user_id:
        user = guest
    else:
        # stub call for what should be sending user info to the API.
        # user = methods.User.get(user_id)
        user = None

    return user

navigation_dictionary_list = [
    {"link": "/", "text": "/index", "glyphicon": "glyphicon-home"},
    {"link": API_HOST, "text": "api", "glyphicon": "glyphicon-cog"},
    {"link": "", "text": "configure page", "glyphicon": "glyphicon-wrench"},
    {"link": "", "text": "save dashboard", "glyphicon": "glyphicon-floppy-disk"},
    {"link": "", "text": "load dashboard", "glyphicon": "glyphicon-open"}
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

    # this should pull from yaml/json or a datastore
    user_layout_panels = [
        {
            "label": "amazon",
            #"height": "",
            #"width": "100%",
            #"position": 0,
            "boxes": [
                {
                    "label": "api status",
                    "height": "100%",
                    "width": "25%",
                    "data": {
                        "enabled": 1,
                        "endpoint": "plugins/aws/status",
                        "update_method": {"type": "polling", "interval_seconds": 30}
                    },
                }
            ]
        }
    ]

    # if we don't have a panel, return help.

    return render_template("index.html", panels=user_layout_panels)
