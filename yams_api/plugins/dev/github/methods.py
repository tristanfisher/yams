from yams_api.plugins.dev.api_utils.http_methods import http_requests_get_to_dict
from json import loads


def get_github_status(url="https://status.github.com/api/status.json"):

    # github's status API is cool -- you can get an enumeration of endpoints from:  https://status.github.com/api.json
    # what status/messages are mapped from https://status.github.com/api/messages.json

    r = http_requests_get_to_dict(url)

    _resp = {
        "response": dict(),
        "headers": dict(),
        "status": "ok"
    }

    _filtered_headers = {
        "date": r.headers.get("date", ""),
        "etag": r.headers.get("etag", ""),
        "status_code": r.headers.get("status_code", 200)
    }

    _resp["headers"] = _filtered_headers

    if not r.error and r.http_2xx:
        _rjson = loads(r.text)
        status_string = _rjson.get("status", "").strip()

        _resp["response"] = status_string

        if status_string != "good":
            _resp["status"] = "nok"

    else:
        _resp["status"] = "nok"

    return str(_resp)


if __name__ == "__main__":
    print(get_github_status())