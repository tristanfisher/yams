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
from flask.ext.sqlalchemy import SQLAlchemy
from config import SETUP, APP, API, PREFERRED_URL_SCHEME
from yams_api.utils.logger import logfile

API_HOST = "%s://%s:%s" % (PREFERRED_URL_SCHEME, API.LISTEN_HOST, API.LISTEN_PORT)

app = Flask(__name__)
app.config.from_object(os.environ.get("FLASK_CONFIG") or "config")
<<<<<<< HEAD

# this should only be used for db operations related to the web interface.
# if you are associating models with this, you more than likely want the API DB.
app_db = SQLAlchemy(app)
db = SQLAlchemy(app)

navigation_dictionary_list = [{"link": "/", "text": "/index"}, {"link": API_HOST, "text": "api"}]

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
    logfile.critical("Failed to load core version: %s" % e)
    exit(1)


@app.route('/')
def index():
    return render_template("index.html")
