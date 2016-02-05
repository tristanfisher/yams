#!/usr/bin/env python
import os
import sys
try:
    from flask.ext.script import Manager, Server
except ImportError as e:
    print("You either need to activate your virtualenv or install YAMS dependencies.")
    sys.exit("Exception: %s" % e)

from config import APP
from yams.app import app
manager_app = Manager(app)

from manage_api import manager_api
from manage_database import manager_database

# app config binding
app.config.from_object(os.environ.get("FLASK_CONFIG") or "config")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

manager_app.add_command(
    "run",
    Server(
        use_debugger=APP.DEBUG,
        use_reloader=APP.DEBUG,
        host=APP.LISTEN_HOST,
        port=APP.LISTEN_PORT
    )
)


manager_app.add_command("api", manager_api)
manager_app.add_command("database", manager_database)

if __name__ == "__main__":
    manager_app.run()