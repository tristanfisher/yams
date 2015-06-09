import os
from yams import app
from config import APP

app.config.from_object(os.environ.get("FLASK_CONFIG") or "config")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

if __name__ == "__main__":
    app.run(host=APP.LISTEN_HOST, port=APP.LISTEN_PORT, debug=APP.DEBUG)
