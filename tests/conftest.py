import os
from pathlib import Path

import pytest

from finance.application import create_app
from finance.database import DB

here = Path(__file__)
project_base = here.parent.parent


@pytest.fixture()
def db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data").joinpath("finance_test.db")
    os.environ["DATABASE"] = "sqlite:///{}".format(db_path)
    db = DB(os.environ["DATABASE"])
    db.create_tables(project_base.joinpath("finance/schema.sql"))

    return db


@pytest.fixture()
def app(db):
    """Instance of Main flask app"""
    app = create_app()
    app.db = db
    app.config.update({"TESTING": True})
    yield app
