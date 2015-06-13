import os
import multiprocessing
import platform
import random
import redis
import string
import tempfile
from easyos import easyos

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True if easyos["os"] == "Darwin" else False


########################################################
# Namespaced vars


class Internal():
    TRUSTED_PROXIES = {"127.0.0.1"}


class APP:
    LISTEN_HOST = "127.0.0.1"
    LISTEN_PORT = 5000
    DEBUG = DEBUG

    DATADIR = os.path.join(basedir, "yams_api", "data")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "yams.sqlite")


class API:
    LISTEN_HOST = "127.0.0.1"
    LISTEN_PORT = 5001
    DEBUG = DEBUG

    DATADIR = os.path.join(basedir, "yams_api", "data")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "yams_api.sqlite")



class AUTH:
    GOOGLE = {
        'id': '_x',
        'secret': '_y'
    }


class TEST:
    APP_SQLALCHEMY_DATABASE_URI = tempfile.mkstemp()
    API_SQLALCHEMY_DATABASE_URI = tempfile.mkstemp()


class SETUP:
    version = "0.01-nightly"


# If we have redis, we have rate limiting available
try:
    r = redis.Redis()
    r.ping()
    USE_RATE_LIMITS = True
except redis.ConnectionError:
    USE_RATE_LIMITS = False


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

# https for url_for, etc. otherwise, _scheme="https" can be passed to url_for
# http://stackoverflow.com/questions/14810795/flask-url-for-generating-http-url-instead-of-https
PREFERRED_URL_SCHEME = "https" if DEBUG else "http"

# deal with unicode now, in year 2015.
JSON_AS_ASCII = False
JSONIFY_PRETTYPRINT_REGULAR = not DEBUG


# Put some of the structured settings back into the scope of the built-in
SQLALCHEMY_DATABASE_URI = APP.SQLALCHEMY_DATABASE_URI