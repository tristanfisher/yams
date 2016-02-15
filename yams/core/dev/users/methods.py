# pseudo db object for interacting with API and flask-login
# https://flask-login.readthedocs.org/en/latest/#your-user-class

# feel free to import this to get the default behaviors on the required methods
#from flask.ext.login import UserMixin
from collections import namedtuple
from flask.ext.login import UserMixin, AnonymousUserMixin
from requests import get as r_get
from requests import post as r_post
import yams.core as _yc
API_HOST = _yc.API_HOST


user_params = ['id', 'name', 'email', 'token', 'is_authenticated', 'active']
UserProps = namedtuple('user', user_params)


class User(UserMixin):
    """An intermediary state to calling the DB for a YAMS user.  Future plans need to support querying
    multiple sources, which is why this is a middleware -- e.g. calling the User model and a node classifier.

    Further, this should support calling over to the API or another source
    (e.g. if the user wants to use LDAP)

    """

    def __init__(self, first_name=None, username=None, email=None, password_from_web=None, supplied_token=None):
        self.id = None
        self.first_name = first_name
        self.username = username
        self.email = email
        self.password_from_web = password_from_web
        self.token = supplied_token
        self.yams_queried_user_obj = self.user_object_from_db

    def is_active(self):
        # pulling this one out of the super class because it's really important to implement
        return True

    def token_valid(self):
        if self.token == self.yams_queried_user_obj.token:
            return True

    def create_account(self):
        r = r_post(
            API_HOST+"/core/user/create",
            data={
                "email": self.email,
                "first_name": self.first_name,
                "password": self.password_from_web
            }
        )
        print("sending!")
        if not str(r.status_code).startswith("2"):
            raise ValueError("Account possibly already exists for that e-mail address.")
        return True

    @property
    def user_object_from_db(self):
        # todo: actually call the upstream auth source
        return UserProps(
            1,
            'test_user',
            'noreply@example.org',
            '',
            True,
            True
        )


    @property
    def to_properties(self):
        # ['id', 'name', 'email', 'is_authenticated', 'active']
        if self.is_active():
            return UserProps(
                self.id,
                self.username,
                self.email,
                self.token,
                self.is_authenticated(),
                self.is_active()
            )


class YAMSAnonymousUser(AnonymousUserMixin):

    # accept whatever, we're going to return an anonymous user
    def __init__(self, *args, **kwargs):
        self.id = 0
        self.username = 'guest'
        self.email = None
        self.token = None

    @property
    def to_properties(self):
        return UserProps(
            self.id,
            self.username,
            self.email,
            self.token,
            self.is_authenticated(),
            self.is_active()
        )

def confirm_token(token):
    # send off token for confirmation in API
    pass