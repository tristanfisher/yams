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
from flask import Flask, Blueprint
from flask import jsonify, redirect, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from config import SETUP, APP
from yams_api.utils.logger import logfile

app = Flask(__name__)
db = SQLAlchemy(app)

# Load the version of core specified by the user to pin
try:
    __import__("yams_api.core.%s" % APP.API_VERSION_CORE)
except ImportError as e:
    logfile.critical("Failed to load core version: %s" % e)
    exit(1)


@app.route('/')
def index():
    return SETUP.version