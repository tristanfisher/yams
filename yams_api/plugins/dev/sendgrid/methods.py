from lxml.html import fromstring as html_string
from yams_api.plugins.dev.api_utils.http_methods import http_requests_get_to_dict


def get_sendgrid_status(url="http://status.sendgrid.com"):

    r = http_requests_get_to_dict(url)

    _resp = {
        "response": dict(),
        "headers": dict(),
        "status": "ok"
    }

    _filtered_headers = {
        "date": r.headers.get("date", ""),
        "last-modified": r.headers.get("last-modified", ""),
        "etag": r.headers.get("etag", ""),
        "x-request-id": r.headers.get("x-request-id", ""),
        "x-statuspage-version": r.headers.get("x-statuspage-version", ""),
        "status_code": r.headers.get("status_code", 200)
    }
    _resp["headers"] = _filtered_headers

    # sendgrid uses nested service statuses
    _resp["response"]["services"] = dict()

    # not really into this as a list, but will adjust as needed
    _resp["response"]["outages"] = []

    general_page_status_text = ''

    if not r.error and r.http_2xx:

        _rtxml = html_string(r.text)
        _body = _rtxml.xpath("//html/body")[0]

        _content_div = _body.xpath("div[contains(@class, 'layout-content')]/div[@class='container']")[0]

        # page structure changes when sendgrid is in an outage
        general_page_status = _content_div.xpath("div[contains(@class, 'page-status')]/span[contains(@class, 'status')]")
        ongoing_incident_div = _content_div.xpath("div[contains(@class, 'unresolved-incidents')]")
        if len(ongoing_incident_div) > 0:

            for _incident in ongoing_incident_div:

                _incident_title_div = _incident.xpath("div[contains(@class, 'unresolved-incident')]/div[contains(@class, 'incident-title')]")
                _incident_text = _incident_title_div[0].xpath("a[contains(@class, 'actual-title')]")[0].text.strip()

                _resp["response"]["outages"].append(_incident_text)

        if len(general_page_status) > 0:
            general_page_status_text = general_page_status[0].text.strip()

        if general_page_status_text == 'All Systems Operational':
            _resp["status"] = "ok"
        else:
            _resp["status"] = "nok"

        # sengrid does a .components-section .components-container, then N- .component-container (note singular)
        by_service_status_divs = _content_div.xpath("div[contains(@class, 'components-section')]/div[contains(@class, 'components-container')]/div[contains(@class, 'component-container')]")

        _serv_status = {}
        for _service in by_service_status_divs:


            # we have to look into child-components container that is at the same level, e.g.
            # <div class="component-container">
            #   <div class="component-inner-container">
            #   <div class="child-components-container"> -> div.component-inner-container -> [span.name, span.component-status]
            #
            # if not, it's simply:
            # <div class="component-container">
            #   <div class="component-inner-container"> -> [span.name, span.component-status]

            _child_components_container = _service.xpath("div[contains(@class, 'child-components-container')]")

            # if we have a child container, move our inspection to the scope of that div.  otherwise, leave
            # at the top level for depth searching
            if len(_child_components_container) > 0:

                # step back to iter point, get name of the service header and make it into a dict for subitem statuses
                _service_name = _service.xpath("div[contains(@class, 'component-inner-container')]/span[contains(@class, 'name')]/span")[1].text.strip()
                _resp["response"]["services"][_service_name] = dict()

                # move our "cursor" to the child components container for searching
                _cursor = _child_components_container

            else:
                # we do not have a child components containiner, so keep the cursor at the loop iter point.
                _cursor = _service

            _service_component_containers = _cursor[0].xpath("div[contains(@class, 'component-inner-container')]")

            for _service_status in _service_component_containers:

                _name = _service_status.xpath("span[@class='name']")[0].text.strip()
                _status = _service_status.xpath("span[@class='component-status']")[0].text.strip()

                if _status == "Operational":
                    _status = "ok"

                _serv_status[_name] = _status

        _resp["response"]["services"] = _serv_status

    else:
        _resp["status"] = "nok"

    return _resp
