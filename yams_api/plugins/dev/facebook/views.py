from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.facebook import methods

@dev_bp.route('/facebook')
def facebook():
    return jsonify()


@dev_bp.route('/facebook/status')
def facebook_status():

    _response = methods.get_facebook_status()

    return jsonify(response=_response)