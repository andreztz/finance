from pathlib import Path

import pytest
from unittest import mock

from werkzeug.security import generate_password_hash

from finance.services import TransactionService


here = Path(__file__)
project_base = here.parent.parent


def fake_lookup(self, symbol):
    symbol = symbol.upper()
    if symbol == "AAAA":
        return {"name": "Stock A", "price": 28.00, "symbol": "AAAA"}
    elif symbol == "BBBB":
        return {"name": "Stock B", "price": 14.00, "symbol": "BBBB"}
    elif symbol == "CCCC":
        return {"name": "Stock C", "price": 2000.00, "symbol": "CCCC"}
    else:
        return None


@pytest.fixture()
def fake_db(db):
    username = "pytest"
    password = "pytest"
    db.create_tables(schema=project_base.joinpath("finance/schema.sql"))
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
        generate_password_hash(password),
    )
    return db


@pytest.fixture()
def transaction():
    return TransactionService()


@mock.patch("finance.services.TransactionService.lookup", fake_lookup)
def test_buy_one_share(transaction, fake_db):
    user_id = 1
    t_id = transaction.buy(1, "AAAA", user_id, fake_db)
    t = fake_db.execute("SELECT * FROM transactions WHERE id=?", t_id)
    assert isinstance(t, list)
    assert len(t) == 1


@mock.patch("finance.services.TransactionService.lookup", fake_lookup)
def test_buy_should_raise_exception_with_wrong_type_param_for_share(
    transaction, fake_db
):
    """transaction.buy() should raise an exception with wrong type param for share"""
    with pytest.raises(TypeError):
        transaction.buy("1", "AAAA", user_id=1, db=fake_db)


@mock.patch("finance.services.TransactionService.lookup", fake_lookup)
def test_buy_should_raise_exception_with_wrong_type_param_for_symbol(
    transaction, fake_db
):
    """transaction.buy() should raise an exception with wrong type param for symbol"""
    with pytest.raises(TypeError):
        transaction.buy("1", 1, user_id=1, db=fake_db)


@mock.patch("finance.services.TransactionService.lookup", fake_lookup)
def test_sell_one_share(transaction, fake_db):
    user_id = 1
    t_id = transaction.buy(1, "AAAA", user_id, fake_db)
    t = fake_db.execute("SELECT * FROM transactions WHERE id=?", t_id)
    assert isinstance(t, list)
    assert len(t) == 1
    t_id = transaction.sell(1, "AAAA", user_id, fake_db)
    t = fake_db.execute("SELECT * FROM transactions WHERE id=?", t_id)
    assert isinstance(t, list)
    assert len(t) == 1
    assert t[0]["shares_qtd"] == -1
