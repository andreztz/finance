from finance.forms import RegistrationForm
from finance.forms import password_is_valid
from finance.forms import username_is_valid


def test_password_is_valid():
    assert password_is_valid("123") is False
    assert password_is_valid("!1a") is False


def test_username_is_valid():
    assert username_is_valid("abc") is False
    assert username_is_valid("!abcd") is False
    assert username_is_valid("abcd-") is False
    assert username_is_valid("abc_") is True


def test_valid_registration_form():
    data = {
        "username": "pytest",
        "password": "pytest123!",
        "confirmation": "pytest123!",
    }
    form = RegistrationForm(**data)
    assert form.validate() is True
    assert len(form.errors) == 0


def test_invalid_registration_form():
    data = {"username": "tes", "password": "123", "confirmation": "1234"}
    form = RegistrationForm(**data)
    assert form.validate() is False
    assert len(form.errors) == 3
    assert (
        form.errors["username"][0]
        == "Field must be between 4 and 10 characters long."
    )
    assert (
        form.errors["username"][1]
        == "Your username must have only letters, numbers or underscores."
    )
    assert form.errors["password"][0] == "The password is not complex enough!"
    assert form.errors["confirmation"][0] == "Passwords must match."
    assert (
        form.errors["confirmation"][1] == "The password is not complex enough!"
    )
