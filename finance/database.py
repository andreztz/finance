import re

from pathlib import Path
from random import choice
from random import randint

from werkzeug.security import generate_password_hash
from cs50 import SQL
import sqlparse
import sqlalchemy
from sqlalchemy.exc import OperationalError


here = Path(__file__)
project_base = here.parent.parent


class DB:
    def __init__(self, url, **kwargs):

        if matches := re.search(r"^sqlite:///(.+)$", url):
            self.filename = Path(matches.group(1))
            if not self.filename.exists():
                self.filename.touch()

        self.sql = SQL(url, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.sql, attr)

    def create_tables(self, schema):
        """
        Create tables from schema.sql
        """
        try:
            with open(schema) as file:
                for line in sqlparse.split(file.read()):
                    self.sql._engine.execute(sqlalchemy.sql.text(line))
        except (OperationalError) as exc:
            if exc.args:
                print(exc.args[0])


def populate(db):

    SYMBOLS = [
        {
            "name": "Meta Platforms Inc - Class A",
            "price": 196.64,
            "symbol": "FB",
        },
        {
            "name": "Principal Exchange-Traded Funds - Principal U.S. Large-Cap Multi-Facto",
            "price": 30.13,
            "symbol": "PLC",
        },
        {
            "name": "Petroleo Brasileiro S.A. Petrobras - ADR",
            "price": 11.83,
            "symbol": "PBR",
        },
        {
            "name": "ProShares Trust - ProShares Ultra MSCI Brazil Capped ETF",
            "price": 21.9886,
            "symbol": "UBR",
        },
        {
            "name": "Telefonica Brasil S.A., - ADR (Representing Ord)",
            "price": 8.82,
            "symbol": "VIV",
        },
    ]

    USERS = ["castrolorena", "fnunes", "bryan35", "pmendes", "afernandes"]

    for username in USERS:
        db.execute(
            """
            INSERT INTO users (
                username,
                hash
            ) VALUES (
                ?, ?
            );
        """,
            username,
            generate_password_hash("test"),
        )

    for symbol in SYMBOLS:
        db.execute(
            """
            INSERT INTO symbols (
                name,
                symbol
            ) VALUES (
                ?, ?
            );
        """,
            symbol.get("name"),
            symbol.get("symbol"),
        )

    for _ in range(10):
        company = choice(SYMBOLS)
        username = choice(USERS)

        user_id = db.execute(
            """SELECT id FROM users WHERE username=?""", username
        )[0]["id"]
        symbol_id = db.execute(
            """SELECT id FROM symbols WHERE symbol=?""", company.get("symbol")
        )[0]["id"]
        price = company.get("price", 0)
        shares_qtd = randint(1, 10)

        purchase = float(price) * shares_qtd

        if purchase <= 10000.00:
            db.execute(
                """
                INSERT INTO transactions (
                    user_id,
                    symbol_id,
                    price,
                    shares_qtd,
                    type
                ) VALUES (
                    ?, ?, ?, ?, ?    
                )
            """,
                user_id,
                symbol_id,
                price,
                shares_qtd,
                "buy",
            )

            cash = db.execute(
                """
                SELECT cash FROM users WHERE id=?
            """,
                user_id,
            )[0]["cash"]

            db.execute(
                "UPDATE users SET cash=? WHERE id=?",
                (cash - purchase),
                user_id,
            )
