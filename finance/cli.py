from pathlib import Path

import click
from flask.cli import with_appcontext

from finance.database import DB
from finance.database import populate


here = Path(__file__)
project_base = here.parent.parent


def create_cli(app):
    @click.command("db-init", help="Create the database.")
    @with_appcontext
    def init_db():
        db = DB(app.config["DATABASE"])
        db.create_tables(project_base.joinpath(("finance/schema.sql")))

    @click.command(
        "db-populate", help="Initialize the database with fake data."
    )
    @with_appcontext
    def populate_db():

        db = DB(app.config["DATABASE"])

        if app.config["ENV"] == "production":
            raise RuntimeError(
                "Fake data can't be created in the production enviroment."
            )

        if app.config["ENV"] == "development":
            try:
                populate(db)
            except RuntimeError:
                app.logger.exception("Database error during population: ")
                app.logger.info(
                    "The database has not yet been created,"
                    "run `flask db-init`."
                )

    app.cli.add_command(init_db)
    app.cli.add_command(populate_db)
