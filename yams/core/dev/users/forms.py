from flask.ext.wtf import Form
import config

from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError


class ValidatorEmailAllowedDomain:
    def __init__(self,
                 user_email,
                 allowed_list=config.Internal.ALLOWED_USER_DOMAINS,
                 message="Sorry, but your e-mail address is not in the allowed domains."):
        self.user_email = user_email
        self.allowed_list = allowed_list
        self.message = message

    def __call__(self, form, field):
        # we've been told to allow anything
        if "*" in self.allowed_list:
            pass
        else:
            # domain portion
            _email = str(self.user_email).split("@")

            try:
                if _email[1] in self.allowed_list:
                    pass
                else:
                    raise ValidationError(self.message)
            except IndexError:
                raise ValidationError("Invalid e-mail address.")


class EmailPasswordForm(Form):
    email = StringField('e-mail', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class EmailSignupForm(EmailPasswordForm):

    first_name = StringField('Your first name', validators=[DataRequired(message="Please tell me your first name.")])












