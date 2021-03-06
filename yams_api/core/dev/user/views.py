from flask import jsonify, request
from yams_api.core.dev import core_bp
from yams_api.core.dev.user import methods
from yams_api.core.dev.user.models import Role, User, Group, UnixPermission


@core_bp.route('/user/', methods=["GET", "POST"])
def core_user():

    # if a POST, see if the user has permission to edit
    # if GET, see if user has permission to read

    return jsonify(status="ok", response="", help=""), 200


@core_bp.route('/user/create', methods=["POST"])
def core_user_create():

    _data = request.get_json()

    email = _data.get('email', None)
    first_name = _data.get('user', None)
    password = _data.get('password', None)

    return jsonify(status="ok", response="")