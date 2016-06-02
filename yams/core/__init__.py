# The versioned endpoints are responsible for generating their own routes.

from config import API, PREFERRED_URL_SCHEME
API_HOST = "%s://%s:%s" % (PREFERRED_URL_SCHEME, API.LISTEN_HOST, API.LISTEN_PORT)