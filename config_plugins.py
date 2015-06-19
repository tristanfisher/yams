# import the secrets file that contains 3rd party auth tokens, etc.
try:
    import secrets
except ImportError:
    print("No secrets file.  If you are using third-party integrations, you may see errors.")

class AWS:

    # not implemented
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    REGION = 'us-east-1'