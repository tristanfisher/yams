#https://developer.constantcontact.com/docs/developer-guides/overview-of-api-endpoints.html
from lxml.html import fromstring as html_string
from yams_api.plugins.dev.api_utils.http_methods import http_requests_get_to_dict


def get_constantcontact_status(url="https://status.constantcontact.com/"):

    # constant contact returns a 403 forbidden when missing headers
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}

    r = http_requests_get_to_dict(url, headers=headers)

    _resp = {
        "response": dict(),
        "headers": dict(),
        "status": "ok"
    }

    _filtered_headers = {
        "date": r.headers.get("date", ""),
        "status_code": r.headers.get("status_code", 200)
    }
    _resp["headers"] = _filtered_headers

    # sendgrid uses nested service statuses
    _resp["response"]["services"] = dict()

    # not really into this as a list, but will adjust as needed
    _resp["response"]["outages"] = []

    if not r.error and r.http_2xx:

        _rtxml = html_string(r.text)
        _body = _rtxml.xpath("//html/body")[0]

        _content_row = _body.xpath("section[@id='status-content']/article/section[@class='entry-content']/section[@class='row']/main/table[contains(@class, 'table')]")

        _tbody_rows = _content_row[0].xpath("tbody/tr")

        _serv_status = {}
        for _service_row in _tbody_rows:

            _service_row_td_collection = _service_row.xpath("td")

            _service_name = _service_row_td_collection[0].text.strip()
            _service_status = _service_row_td_collection[2].text.strip()

            if _service_status == "All Systems are Available and Operating Normally":
                _service_status = "ok"
            else:
                _resp["response"]["outages"].append(_service_name)

            _serv_status[_service_name] = _service_status

        _resp["response"]["services"] = _serv_status

    else:
        _resp["status"] = "nok"

    return _resp
