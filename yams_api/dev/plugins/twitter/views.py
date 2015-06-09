from flask import jsonify
from yams_api.dev import dev_bp


@dev_bp.route('/twitter')
def twitter():
    return jsonify(status="")