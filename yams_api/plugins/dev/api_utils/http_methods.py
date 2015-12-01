from collections import namedtuple
from requests.exceptions import ConnectionError
import requests

# header->dict, text->str, status->int, http_2xx->bool, status_major_code->int, error->bool
HTTPResponse = namedtuple('HTTPResponse', ['headers', 'text', 'status', 'http_2xx', 'status_major_code', 'error'])


def http_requests_get_to_dict(url):
    """Fetch content at a URL, returning a namedtuple of python-request module attributes

    :param url: url to scrape
    :return: a namedtuple containing ('headers', 'text', 'status') for Pythonic scripting
    """

    # Keep these outside of the try/except so we can potentially get metadata even on exceptions.
    # Defines some placeholders to avoid a potential NameError
    _headers = dict()
    _status = 200
    _status_major_code = 0

    try:

        r = requests.get(url)
        # r.content is a bytes obj and probably won't be json serializable.  could return a tuple
        _status = r.status_code
        _str_status = str(_status)
        _status_major_code = int(_str_status[0]) # '200' -> '2' ->2

        rh = r.headers
        rt = r.text

        # common headers
        _headers["status_code"] = _status
        _headers["etag"] = rh.get("etag", "")
        _headers["date"] = rh.get("date", "")
        _headers["last-modified"] = rh.get("last-modified", "")
        _headers["content-type"] = rh.get("content-type", "")
        _headers["raw_headers"] = dict(rh)

        _http_namedtuple = HTTPResponse(
            _headers,
            rt,
            _status,
            (_status_major_code == 2),
            _status_major_code,
            False
        )

    except ConnectionError as e:
        _headers["response"] = str(e)

        _http_namedtuple = HTTPResponse(
            _headers,
            str(e),
            _status,
            (_status_major_code == 2),
            _status_major_code,
            True)

    return _http_namedtuple