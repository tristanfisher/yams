from json import loads
from lxml.html import fromstring as html_string
from yams_api.plugins.dev.api_utils.http_methods import http_requests_get_to_dict

STATUS = {
    0: "nok",
    1: "ok",
}

def get_facebook_status(url="https://www.facebook.com/feeds/api_status.php"):

    # use the status API https://www.facebook.com/feeds/api_status.php
    # if the status api is unavailable, look at the page source to pull out the status
    # be careful not to look post-JS rendering as the DOM is populated from a hidden <code> element

    r = http_requests_get_to_dict(url)

    _resp = {
        "response": dict(),
        "headers": dict(),
        "status": "ok"
    }

    _filtered_headers = {
        "date": r.headers.get("date", ""),
        "expires": r.headers.get("expires", ""),
        "last-modified": r.headers.get("last-modified", ""),
        "etag": r.headers.get("etag", ""),
        "status_code": r.headers.get("status_code", 200),
        "x-fb-debug": r.headers.get("x-fb-debug", ""),
        "pragma": r.headers.get("pragma", ""),
    }
    _resp["headers"] = _filtered_headers

    # not really into this as a list, but will adjust as needed
    _resp["response"]["outages"] = []

    _stat_str = ''
    _stat_int = 0

    if not r.error and r.http_2xx:

        _rjson = loads(r.text)
        _curr = _rjson.get("current", "")

        if _curr:
            _stat_int = _curr.get("health", 0)
            _stat_str = _curr.get("subject", "").strip()

        if _stat_str:
            _resp["response"] = _stat_str

        # get status info or default to the first one
        if _stat_int:
            _resp["status"] = STATUS.get(_stat_int, STATUS[0])

    else:
        _resp["status"] = "nok"

    return _resp
