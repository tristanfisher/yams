from flask import Blueprint, jsonify
from yams.app import app
from yams_api.utils.logger import log

# jumper between blueprints
core_dev_blueprints = []

from .users.views import core_users_bp
core_dev_blueprints.append(core_users_bp)
