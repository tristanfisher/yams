from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.dropbox import methods


@dev_bp.route('/dropbox/')
def dropbox():
    return jsonify()


@dev_bp.route('/dropbox/status')
def dropbox_status():

    _response = methods.get_dropbox_website_status()
    return jsonify(response=_response)