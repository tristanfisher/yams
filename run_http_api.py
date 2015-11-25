#!/usr/bin/env python
import os
from yams_api import api
from config import API

api.config.from_object(os.environ.get("FLASK_API_CONFIG") or "config")
api.jinja_env.trim_blocks = True
api.jinja_env.lstrip_blocks = True

if __name__ == "__main__":
    api.run(host=API.LISTEN_HOST, port=API.LISTEN_PORT, debug=API.DEBUG)
