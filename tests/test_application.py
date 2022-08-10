def test_app_is_created(app):
    assert app.name == "finance.application"


# def test_config_is_loaded(config):
#     """
#     Notes:
#         - `config` is fixture from pytest-flask"""
#     assert config["DEBUG"] is False


def test_request_returns_404(client):
    """
    Notes:
        `- client` is fixture from pytest-flask this client
            run off-linesee
         - see on the web: liveserver
    """
    assert client.get("/missing_url").status_code == 404


def test_register_user(app, client):
    payload = {
        "username": "pytest",
        "password": "test1234!",
        "confirmation": "test1234!",
    }
    client.post("/register", data=payload)
    data = app.db.execute(
        "SELECT * FROM users WHERE username=?", payload["username"]
    )[0]
    assert payload["username"] == data["username"]
    assert data["cash"] == 10000.00
    assert data["hash"]
