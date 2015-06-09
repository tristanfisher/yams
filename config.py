import os
import platform
import random
import redis
import string
import tempfile
from easyos import easyos

basedir = os.path.abspath(os.path.dirname(__file__))

########################################################
# Magic vars

DEBUG = True if easyos["os"] == "Darwin" else False
SECRET_KEY_FILE = basedir + "secret_key"


# If we don't have a secret access key for signing sessions,
# generate one and put it on disk.
def log(*args): print(*args)
try:
    with open(SECRET_KEY_FILE, "r") as f:
        SECRET_KEY = f.read()
except IOError:
    log("Creating secret_key file")
    l = random.randint(25, 50)
    _rand = "".join(random.choice(string.printable) for i in range(l))
    with open(SECRET_KEY_FILE, "w+") as f:
        f.write(_rand)
        SECRET_KEY = f.read()


USE_TOKEN_AUTH = True
WTF_CSRF_ENABLED = not DEBUG

# https for url_for, etc. otherwise, _scheme="https" can be passed to url_for
# http://stackoverflow.com/questions/14810795/flask-url-for-generating-http-url-instead-of-https
# PREFERRED_URL_SCHEME = "https"
# THREADS_PER_PAGE = 8

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