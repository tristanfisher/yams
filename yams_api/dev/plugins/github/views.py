from flask import jsonify
from yams_api.dev import dev_bp


@dev_bp.route('/github')
def github():
    return jsonify(status="")


@dev_bp.route('/github_status')
def github_status():
    return jsonify(status="")