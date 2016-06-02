from yams_api.api import yams_api_conf, api_secret_key
from yams_api.utils import easytime, email, logger
from . import models
from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired

# models.User

# which token to send? api or app or what?

# app could ask the api for a specific token


ts = URLSafeTimedSerializer(api_secret_key)

def create_account():
    pass

def send_email_password_reset():
    pass

def send_email_confirmation():
    pass

def confirm_token(token):
    return True