from lxml.html import fromstring as html_string
from yams_api.plugins.dev.api_utils.http_methods import http_requests_get_to_dict


def get_cloudinary_status(url="http://status.cloudinary.com"):

    # this is only history -- no "we're fine right now" or enumeration of things that are working.
    # http://status.cloudinary.com/history.rss
    # also, as of this writing, there is no standard way to determine the end boundary of an outage, which
    # makes this generally useless for our purposes.


    r = http_requests_get_to_dict(url)

    # response dict - response is data blob to return (e.g. 'Site is normal!'), headers are headers, status is ok/nok
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

        _rtxml = html_string(r.text)
        _body = _rtxml.xpath("//html/body")[0]

        _content_div = _body.xpath("div[contains(@class, 'layout-content')]/div[@class='container']")[0]

        general_page_status_raw_text = _content_div.xpath("div[contains(@class, 'page-status')]/span[contains(@class, 'status')]")[0].text
        general_page_status = general_page_status_raw_text.strip()


        by_service_status_divs = _content_div.xpath("div[contains(@class, 'components-section')]/div[contains(@class, 'components-container')]")[0]

        _serv_status = {}

        for _service in by_service_status_divs:
            _inner_div_group = _service.xpath("div[contains(@class, 'component-inner-container')]")[0]
            _name = _inner_div_group.xpath("span[@class='name']")[0].text.strip()
            _status = _inner_div_group.xpath("span[@class='component-status']")[0].text.strip()
            if _status == "Operational":
                _status = "ok"

            _serv_status[_name] = _status

        _resp["response"]["services"] = _serv_status

        if general_page_status == 'All Systems Operational':
            _resp["status"] = "ok"

    else:
        _resp["status"] = "nok"

    return _resp