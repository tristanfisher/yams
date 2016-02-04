from flask import jsonify
from yams_api.core.dev import core_bp
from yams_api.core.dev.dashboard import methods
from yams_api.core.dev.dashboard.models import yamsBox, yamsBoxGroup, yamsBoxPanel, UnixPermission

@core_bp.route('/dashboard/', methods=["GET", "POST"])
def core_dashboard():

    # if a POST, see if the user has permission to edit
    # if GET, see if user has permission to read

    return jsonify(status="ok", response="", help="")
