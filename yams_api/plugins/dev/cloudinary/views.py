from flask import jsonify
from yams_api.plugins.dev import dev_bp
from yams_api.plugins.dev.cloudinary import methods

@dev_bp.route('/cloudinary')
def cloudinary():
    return jsonify()


@dev_bp.route('/cloudinary/status')
def cloudinary_status():

    _response = methods.get_cloudinary_status()

    return jsonify(response=_response)