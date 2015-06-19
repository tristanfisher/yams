from flask import Blueprint, jsonify, render_template
from yams.app import app
from yams_api.utils.logger import logfile

core_users_bp = Blueprint("core_users", __name__, url_prefix="/users")


@core_users_bp.route("/", defaults={"id": "*"})
@core_users_bp.route("/<int:id>/")
def core_index(id):
    return render_template("/core/dev/users.html")