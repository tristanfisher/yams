import requests
from requests.exceptions import ConnectionError
from lxml.html import fromstring as html_string

# Dropbox Community post that notes why we're scraping instead of using an API.
# https://www.dropboxforum.com/hc/en-us/community/posts/202225545-Dropbox-Core-API-status

def get_dropbox_website_status(url="https://status.dropbox.com/"):

    _resp = {
        "response": dict(),
        "headers": dict()
    }

    try:
        r = requests.get(url)

        rc = r.status_code
        rt = r.text
        rheaders = r.headers

        # headers we should expect from dropbox
        _resp["headers"]["status_code"] = rc
        _resp["headers"]["date"] = rheaders.get("date", "")
        _resp["headers"]["etag"] = rheaders.get("etag", "")

        if str(rc).startswith("2"):

            if "json" in rheaders["content-type"]:
                _resp["response"] = "unexpected content-type.  expected text/html.  (good news -- we can update our plugin!)"
            else:
                _rtxml = html_string(rt)
                _rtxml_status_line = _rtxml.xpath('//html/body/div[@id="status-line"]/h1')[0]
                _rtxml_status_block = _rtxml_status_line.text

                if _rtxml_status_block == "Dropbox is running normally.":
                    _resp["status"] = "ok"

                _resp["response"] = str(_rtxml_status_block)

            return _resp

    except ConnectionError as e:
        _resp["response"] = str(e)

    # if ConnectionError exception or not an http 2xx
    _resp["status"] = "nok"

    return _resp