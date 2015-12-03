from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.sendgrid import methods

@dev_bp.route('/sendgrid')
def sendgrid():
    return jsonify()


@dev_bp.route('/sendgrid/status')
def sendgrid_status():

    _response = methods.get_sendgrid_status()

    return jsonify(response=_response)