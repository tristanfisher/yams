from flask import jsonify, request
from yams_api.plugins.dev import dev_bp
import requests
import requests as r

@dev_bp.route("/http")
def http():
    return jsonify(status="")

# todo: usage on route /http/replay/

# from requests import get, head, post, patch, put, delete, options
@dev_bp.route("/http/replay/<method>", methods=["POST", "GET", "PUT", "OPTIONS"])
def http_replay(method):
    """Replay an incoming request of type <method> against the parameter list of endpoints"""

    endpoint_list = request.args.get("host", "")
    endpoint_list = endpoint_list.split(";")
    timeout = request.args.get("timeout", None) or 5

    #_method = requests.__getattribute__(method.lower())

    if not endpoint_list:
        return jsonify(status=500,
                       message="Expected parameters in the form of ?host=http://host/path;host=http://host2/path")
    else:
        # create an async model when we actually need it, not sooner

        responses = []

        for ep in endpoint_list:
            try:
                _r = requests.__getattribute__(method.lower())(ep, timeout=timeout)

                status_code = _r.status_code
            except r.exceptions.Timeout:
                status_code = 408  # request timeout
            except r.exceptions.RequestException:
                status_code = 520

            responses.append(status_code)

        _r_status = set(responses)

        if len(_r_status) == 1 and _r_status.pop == 200:
            # maybe 203 "non-authoritative" is better?
            status = 200
        else:
            # 520 "unknown error" fine?
            status = 520

        return jsonify(status=status)