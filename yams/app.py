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

import os
from flask import Flask, Blueprint
from flask import jsonify, redirect, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from config import SETUP


app = Flask(__name__)
db = SQLAlchemy(app)
from yams_api import models


@app.route('/')
def index():
    return SETUP.version