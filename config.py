import os
import random
import redis
import string
import tempfile
from easyos import easyos
from config_loader import chain_load_setting

# chain_load_setting goes in order of envvar, settings file, default.  chain_load_setting(config_file_option, envvar, default)

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True if easyos["os"] == "Darwin" else False


########################################################
# Namespaced vars


class Internal():
    TRUSTED_PROXIES = {"127.0.0.1"}


class APP:

    LISTEN_HOST = chain_load_setting("APP_HOST", "YAMS_APP_HOST", "127.0.0.1")
    LISTEN_PORT = chain_load_setting("APP_PORT", "YAMS_APP_PORT", default=1110)

    DEBUG = DEBUG

    API_VERSION_CORE = chain_load_setting("API_VERSION_CORE", "YAMS_API_VERSION_CORE", default="dev")
    API_VERSION_PLUGINS = chain_load_setting("API_VERSION_PLUGINS", "YAMS_API_VERSION_PLUGINS", default="dev")

    default_datadir = os.path.join(basedir, "yams_api", "data")
    DATADIR = chain_load_setting("API_DATADIR", "YAMS_API_DATADIR", default=default_datadir)

    default_database = "sqlite:///" + os.path.join(basedir, "yams.sqlite")
    SQLALCHEMY_DATABASE_URI = chain_load_setting("APP_DATABASE_URI", "YAMS_APP_DATABASE_URI", default=default_database)

    SITE_NAME = chain_load_setting("APP_REBRANDING_NAME", "YAMS_REBRANDING_NAME", default="YAMS")


class API:

    LISTEN_HOST = chain_load_setting("API_HOST", "YAMS_API_HOST", "127.0.0.1")
    LISTEN_PORT = chain_load_setting("API_PORT", "YAMS_API_PORT", default=1111)

    # ----------------------------------------- #
    # ---- Socket API ---- #
    LISTEN_PORT_SOCKET = chain_load_setting("API_SOCKET_PORT", "YAMS_API_SOCKET_PORT", default=1112)

    # Yield epsilon is to avoid busy-waiting.  0 denotes yielding to any ready thread.  See scheduler docs.
    # I've found 0 to fully utilize a core, so defaults to a longer interval to save electricity.
    YIELD_TO_READY_THREADS=0
    SOCKET_THREAD_YIELD_EPSILON = 0.25
    SOCKET_TIMEOUT_SECONDS = 30
    SOCKET_RX_BUFFER_BYTES = 4096

    # ----------------------------------------- #

    DEBUG = DEBUG

    API_VERSION_CORE = chain_load_setting("API_VERSION_CORE", "YAMS_API_VERSION_CORE", default="dev")
    API_VERSION_PLUGINS = chain_load_setting("API_VERSION_PLUGINS", "YAMS_API_VERSION_PLUGINS", default="dev")

    default_datadir = os.path.join(basedir, "yams_api", "data")
    DATADIR = chain_load_setting("API_DATADIR", "YAMS_API_DATADIR", default=default_datadir)

    default_database = "sqlite:///" + os.path.join(basedir, "yams_api.sqlite")
    SQLALCHEMY_DATABASE_URI = chain_load_setting("API_DATABASE_URI", "YAMS_API_DATABASE_URI", default=default_database)


    # If we have redis, we have rate limiting available
    try:
        r = redis.Redis()
        r.ping()
        USE_RATE_LIMITS = True
    except redis.ConnectionError:
        USE_RATE_LIMITS = False


class ThirdParty:

    # Envvars probably from a .profile or vars injected in the startup script (e.g. export aws_access_key_id='xxx')
    # You can set ~/.aws/credentials to aws_access_key_id = ${AWS_ACCESS_KEY_ID}, etc.
    AWS_ACCESS_KEY_ID = chain_load_setting("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = chain_load_setting("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY", None)
    AWS_DEFAULT_REGION = 'us-east-1'


class TEST:
    APP_SQLALCHEMY_DATABASE_URI = tempfile.mkstemp()
    API_SQLALCHEMY_DATABASE_URI = tempfile.mkstemp()


class SETUP:
    from version import version
    version = version


########################################################
# Magic vars

# Be sure not to shadow any of the built-in config values listed here:
# http://flask.pocoo.org/docs/latest/config/#builtin-configuration-values

def return_or_make_secret_key(secret_key_file):
    # If we don't have a secret access key for signing sessions,
    # generate one and put it on disk.

    try:
        with open(secret_key_file, "r") as f:
            return f.read()
    except IOError:

        print("Creating secret_key file")

        l = random.randint(25, 50)
        _rand = "".join(random.choice(string.printable) for i in range(l))
        with open(secret_key_file, "w+") as f:
            f.write(_rand)
            return f.read()

SECRET_KEY = return_or_make_secret_key(basedir + "/secret_key")
SESSION_COOKIE_NAME = "yams_session"

USE_TOKEN_AUTH = True
WTF_CSRF_ENABLED = not DEBUG

# https for url_for, etc. otherwise, _scheme="https" can be passed to url_for.  You are reverse-proxying, right?
# http://stackoverflow.com/questions/14810795/flask-url-for-generating-http-url-instead-of-https
PREFERRED_URL_SCHEME = chain_load_setting("PREFERRED_URL_SCHEME", "YAMS_PREFERRED_URL_SCHEME", "http")

# deal with unicode now
JSON_AS_ASCII = False
JSONIFY_PRETTYPRINT_REGULAR = not DEBUG

# Put some of the structured settings back into the scope of the built-in
SQLALCHEMY_DATABASE_URI = APP.SQLALCHEMY_DATABASE_URI
DEFAULT_LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

# Import the plugin configuration
from config_plugins import *
