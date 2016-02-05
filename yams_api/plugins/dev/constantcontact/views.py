from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.constantcontact import methods

@dev_bp.route('/constantcontact')
def constantcontact():
    return jsonify()


@dev_bp.route('/constantcontact/status')
def constantcontact_status():

    _response = methods.get_constantcontact_status()

    return jsonify(response=_response)