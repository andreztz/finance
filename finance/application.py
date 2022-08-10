import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import (
    default_exceptions,
    HTTPException,
    InternalServerError,
)
from werkzeug.security import check_password_hash, generate_password_hash


from .cli import create_cli
from .database import DB
from .helpers import apology, login_required, lookup, usd
from .services import TransactionService
from .services import NotEnoughMoneyError
from .services import InvalidTickerSymbolError
from .forms import RegistrationForm


def create_app():
    # Configure application
    app = Flask(__name__)

    load_dotenv()
    create_cli(app)

    # Ensure templates are auto-reloaded
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers[
            "Cache-Control"
        ] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Custom filter
    app.jinja_env.filters["usd"] = usd

    # Configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    Session(app)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Configure Debug Toolbar
    # https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration
    app.config["DEBUG_TB_HOSTS"] = ["127.0.0.1"]
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
    app.config["DEBUG_TB_TEMPLATE_EDITOR_ENABLED"] = True
    app.config["DEBUG_TB_PROFILER_ENABLED"] = True

    DebugToolbarExtension(app)

    # Configure CS50 Library to use SQLite database
    # db = SQL("sqlite:///{}".format(app.config["DATABASE"]))
    app.config["DATABASE"] = os.getenv("DATABASE")
    db = DB(app.config["DATABASE"])

    # Make sure API key is set
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")

    service = TransactionService()

    @app.route("/")
    @login_required
    def index():
        """Show portfolio of stocks"""
        user_id = session.get("user_id")

        shares = db.execute(
            """
            SELECT name, symbol, price, shares_qtd, SUM(shares_qtd) as total FROM users 
                JOIN transactions ON users.id = transactions.user_id
                JOIN symbols ON symbols.id = transactions.symbol_id
                WHERE users.id=? GROUP by symbols.id
        """,
            user_id,
        )

        cash = db.execute(
            """
            SELECT cash FROM users WHERE id=?
        """,
            user_id,
        )[0]["cash"]

        for share in shares:
            stock = lookup(share.get("symbol")) or {}
            share["price"] = stock.get("price", 0)

        return render_template("index.html", shares=shares, cash=cash)

    @app.route("/buy", methods=["GET", "POST"])
    @login_required
    def buy():
        """Buy shares of stock"""
        if request.method == "GET":
            return render_template("buy.html")

        quantity = request.form["shares"]
        symbol = request.form["symbol"].strip().upper()

        try:
            service.buy(int(quantity), symbol, session.get("user_id"), db)
        except TypeError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("buy.html"), 400
        except ValueError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("buy.html"), 400
        except InvalidTickerSymbolError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("buy.html"), 400
        except NotEnoughMoneyError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("buy.html"), 400
        except Exception:
            app.logger.exception("Internal server error ")
            return apology("Internal server error."), 500
        else:
            flash("Bought!")
            return redirect("/")
        # Na busca sql é possivel interpolar variaveis
        # com ? ou :id  one :id seria o mesmo que parametros nomeados???

    @app.route("/history")
    @login_required
    def history():
        """Show history of transactions"""
        user_id = session.get("user_id")

        transactions = db.execute(
            """
            SELECT name, symbol, price, shares_qtd, created_at FROM users 
                JOIN transactions ON users.id = transactions.user_id
                JOIN symbols ON symbols.id = transactions.symbol_id
                WHERE users.id=? ORDER BY created_at
        """,
            user_id,
        )

        return render_template("history.html", transactions=transactions)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""
        # Forget any user_id
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 403)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 403)

            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?",
                request.form.get("username"),
            )

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form["password"]
            ):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    @app.route("/logout")
    def logout():
        """Log user out"""
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    @app.route("/quote", methods=["GET", "POST"])
    @login_required
    def quote():
        """Get stock quote."""
        if request.method == "GET":
            return render_template("quote.html")

        symbol = request.form.get("symbol", "").strip().upper()

        try:
            stock = service.lookup(symbol)
        except InvalidTickerSymbolError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("quote.html"), 400
        else:
            return render_template("quote.html", stock=stock)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Register user"""

        form = RegistrationForm(request.form or None)

        if request.method == "GET":
            return render_template("register.html", form=form)

        username_exists = db.execute(
            "SELECT username FROM users WHERE username=?",
            request.form["username"],
        )
        if username_exists:
            flash("Username is already registered.")

        if form.validate() and not username_exists:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                form.data["username"],
                generate_password_hash(form.data["password"]),
            )
            return redirect("/login")

        return render_template("register.html", form=form), 400

    @app.route("/sell", methods=["GET", "POST"])
    @login_required
    def sell():
        """Sell shares of stock"""
        user_id = session.get("user_id")
        if request.method == "GET":
            data = db.execute(
                """
                SELECT DISTINCT(symbol) FROM users
                    JOIN transactions ON users.id = transactions.user_id
                    JOIN symbols ON symbols.id = transactions.symbol_id 
                    WHERE users.id = ?
            """,
                user_id,
            )  # TODO: substitui validação shares > 0 com GROUP BY symbol HAVING SUM(shares) > 0
            return render_template(
                "sell.html", symbols=[row["symbol"] for row in data]
            )

        quantity = request.form["shares"]
        symbol = request.form["symbol"].strip().upper()

        try:
            service.sell(int(quantity), symbol, user_id, db)
        except TypeError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("sell.html"), 400
        except ValueError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("sell.html"), 400
        except InvalidTickerSymbolError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("sell.html"), 400
        except NotEnoughMoneyError as exc:
            if message := exc.args[0]:
                flash(message)
            return render_template("sell.html"), 400
        except Exception:
            app.logger.exception("Internal server error ")
            return apology("Internal server error."), 500
        else:
            flash("Sold!")
            return redirect("/")

    def errorhandler(e):
        """Handle error"""
        if not isinstance(e, HTTPException):
            e = InternalServerError()
        return apology(e.name, e.code)

    # Listen for errors
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)

    return app
