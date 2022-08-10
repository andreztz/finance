from .helpers import lookup


class TransactionBaseError(Exception):
    pass


class NotEnoughMoneyError(TransactionBaseError):
    def __init__(self):
        super().__init__("Don't have enough money.")


class NotEnoughStockSharesError(TransactionBaseError):
    def __init__(self):
        super().__init__("Don't have enough stock shares.")


class InvalidTickerSymbolError(TransactionBaseError):
    def __init__(self, symbol):
        super().__init__(
            f"The symbol ({symbol}) does not exist, You must enter a valid symbol."
        )


class TransactionService:
    def buy(self, quantity, symbol, user_id, db):
        """Buy shares

        Args:
            quantity (int): Number of shares to buy
            symbol (str): Stock ticker symbol
            user_id (int): User id
            db (:obj: `finance.database.DB`): Database instance

        Returns:
            transaction_id (int): Transaction id
        """
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer.")

        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer.")

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero.")

        if quantity <= 0:
            raise ValueError("quantity must be greater than zero.")

        stock = self.lookup(symbol)

        try:
            symbol_id = db.execute(
                "SELECT id FROM symbols WHERE symbol=?", symbol
            )[0]["id"]
        except:
            symbol_id = db.execute(
                "INSERT OR REPLACE INTO symbols (name, symbol) values(?, ?)",
                stock["name"],
                stock["symbol"],
            )

        cash = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0][
            "cash"
        ]
        price = stock["price"]
        purchase_order = quantity * price

        if cash < purchase_order:
            raise NotEnoughMoneyError()

        cash = cash - purchase_order

        db.execute("UPDATE users SET cash=? WHERE id=?", cash, user_id)

        t_id = db.execute(
            """
            INSERT INTO transactions (user_id, symbol_id, price, shares_qtd, type)
                VALUES (?,?,?,?,?)""",
            user_id,
            symbol_id,
            price,
            quantity,
            "buy",
        )

        return t_id

    def sell(self, quantity, symbol, user_id, db):
        """Sell shares

        Args:
            quantity (int): Number of shares to sell
            symbol (str): Stock ticker symbol
            user_id (int): User id
            db (:obj: `finance.database.DB`)

        Returns:
            transaction_id (int): Transaction id
        """
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer.")

        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer.")

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero.")

        if quantity <= 0:
            raise ValueError("quantity must be greater than zero.")

        stock = self.lookup(symbol)

        # TODO: validação de shares > 0 direto na consulta sql com:
        # GROUP BY symbol HAVING SUM(shares) > 0;
        shares = db.execute(
            """
            SELECT SUM(shares_qtd) as total FROM users 
                JOIN transactions ON users.id = transactions.user_id
                JOIN symbols ON symbols.id = transactions.symbol_id 
                WHERE users.id=? AND symbols.symbol=? GROUP BY symbol
        """,
            user_id,
            symbol,
        )[0]["total"]

        if not shares:
            raise NotEnoughStockSharesError()

        if quantity > shares:
            raise NotEnoughStockSharesError()

        price = stock["price"]
        cash_available = db.execute(
            "SELECT cash FROM users WHERE id=?", user_id
        )[0]["cash"]
        sales_order = quantity * price
        cash = cash_available + sales_order
        db.execute("UPDATE users SET cash=? WHERE id=?", cash, user_id)
        symbol_id = db.execute(
            "SELECT id FROM symbols WHERE symbol=?", symbol
        )[0]["id"]
        t_id = db.execute(
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
            (-1) * quantity,
            "sell",
        )
        return t_id

    def history(self):
        pass

    def lookup(self, symbol):
        """Look up quote for stock ticker symbol
        Args:
            symbol (str): Stock ticker symbol

        Returns:
            (:obj: `dict`): Stock info like (name, symbol, price...)
        """
        stock = lookup(symbol)
        if stock is None:
            raise InvalidTickerSymbolError(symbol)
        return stock
