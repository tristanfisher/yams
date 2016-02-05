import os
from flask.ext.script import Manager, Server
from yams_api import api
from config import API

api.config.from_object(os.environ.get("FLASK_API_CONFIG") or "config")
api.jinja_env.trim_blocks = True
api.jinja_env.lstrip_blocks = True

manager_api = Manager(api, usage="API Management")

# todo: once the socket API changes are public, make this default to starting that as well
manager_api.add_command(
    "run",
    Server(
        use_debugger=API.DEBUG,
        use_reloader=API.DEBUG,
        host=API.LISTEN_HOST,
        port=API.LISTEN_PORT
    ),
)

manager_api.add_command(
    "run_http_only",
    Server(
        use_debugger=API.DEBUG,
        use_reloader=API.DEBUG,
        host=API.LISTEN_HOST,
        port=API.LISTEN_PORT
    ),
)