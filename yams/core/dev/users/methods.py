# pseudo db object for interacting with API and flask-login
# https://flask-login.readthedocs.org/en/latest/#your-user-class
class User:

    def __init__(self, user_object):
        self.user_object = user_object

    def is_authenticated(self):
        # True if user has valid creds.  only authed users
        # fulfill the app's login_required
        return self.user_object.is_authenticated

    def is_active(self):
        return self.user_object.active

    def get_id(self):
        # must be unicocde
        return self.user_object.id

    def is_anonymous(self):
        # return True if anonymous/guest user
        return False