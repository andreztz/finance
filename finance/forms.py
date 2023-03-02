import re

from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import Length
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError


def password_is_valid(password):
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
    return True if re.match(pattern, password) else False


def username_is_valid(username):
    pattern = r"^(?=.*)[A-Za-z_0-9]{4,10}$"
    return True if re.match(pattern, username) else False


def validate_username(_, username):
    if not username_is_valid(username.data):
        raise ValidationError(
            "Your username must have only letters, numbers or underscores."
        )
    return True


def validate_password(_, password):
    if not password_is_valid(password.data):
        raise ValidationError("The password is not complex enough!")
    return True


class RegistrationForm(Form):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, max=10),
            validate_username,
        ],
        render_kw={
            "autofocus": True,
            "autocomplete": "off",
            "class": "form-control",
            "placeholder": "Username",
            "id": "username",
        },
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            validate_password,
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Password",
            "id": "password",
        },
    )
    confirmation = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
            validate_password,
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Confirm Password",
            "id": "confirmation",
        },
    )
