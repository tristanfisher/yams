from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.github import methods

@dev_bp.route('/github')
def github():
    return jsonify()


@dev_bp.route('/github/status')
def github_status():

    _response = methods.get_github_status()

    return jsonify(response=_response)