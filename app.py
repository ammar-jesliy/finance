import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    sum = 0

    # find a way to extract the total of the transaction from a single type of share so you can print the details in a loop

    # store the total of one type of share owned by the user in a dictionary
    look = db.execute("SELECT symbol, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])

    # update the latest prices
    for i in range(len(look)):
        current = lookup(look[i]["symbol"])
        price = current["price"]
        total = look[i]["SUM(amount)"] * price
        sum = sum + total
        db.execute("UPDATE transactions SET current_price = ?, total = ? WHERE symbol = ? AND user_id = ?", price, total, look[i]["symbol"], session["user_id"])

    # store information to print in the table in index.html through a loop
    rows = db.execute("SELECT symbol, name, SUM(amount), current_price, total FROM transactions WHERE user_id = ? AND total <> 0 GROUP BY symbol", session["user_id"])


    # extract cash balance
    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    if len(balance) == 0:
        return redirect("/login")

    cash = balance[0]["cash"]

    # total of the cash remaining and stocks in hand
    sum = sum + cash

    return render_template("index.html", rows=rows, cash=cash, sum=sum)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        stock_info = lookup(request.form.get("symbol"))
        amount = float(request.form.get("shares"))
        now = datetime.now()
        time = now.strftime("%d-%m-%Y %H:%M:%S")

        if stock_info == None:
            return apology("incorrect symbol")

        if amount < 1:
            return apology("invalid amount")

        if not isinstance(amount, int):
            return apology("invalid amount")

        # subtract the cash used for the transaction from the total cash the user has.
        row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        cash_rem = row[0]["cash"]

        total = stock_info["price"] * amount

        # if the remaining cash is less than the cash used for the transaction, return an apology
        if cash_rem < total:
            return apology("u brokie")

        # insert the values into the transaction table
        db.execute("INSERT INTO transactions (user_id, symbol, name, amount, price, current_price, total, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], stock_info["symbol"], stock_info["name"], amount, stock_info["price"], stock_info["price"], total, time)

        # subtract the cash used for transaction from the cash remaining
        balance = cash_rem - stock_info["price"] * amount

        # update the cash balance to the database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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
    if request.method == "POST":
        # display the price after looking up the symbol
        symbol = request.form.get("symbol")
        quote = lookup(symbol)

        if quote == None:
            return apology("incorrect symbol")

        return render_template("quoted.html", quote=quote)

    else:
        # display form to get quote
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # input user data to database
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("enter a username")

        if not password:
            return apology("enter a password")

        if password != confirmation:
            return apology("confirm password")

        other = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(other) != 0:
            return apology("username exists")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        return redirect("/")

    else:
        # display register form
        return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # store the symbools of stocks owned by the user in a dict
    rows = db.execute("SELECT symbol FROM transactions WHERE user_id = ? AND total <> 0 GROUP BY symbol", session["user_id"])

    if request.method == "POST":
        stock_info = lookup(request.form.get("symbol"))
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # calculate amount of shares as negative because we are selling shares
        neg = shares * (-1)
        total = stock_info["price"] * neg

        # transaction time
        now = datetime.now()
        time = now.strftime("%d-%m-%Y %H:%M:%S")

        # store the remaining shares of a company in a dict
        rem = db.execute("SELECT symbol, SUM(amount) FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", session["user_id"], symbol)

        # validate the input
        if shares < 1:
            return apology("invalid amount")

        if shares > rem[0]["SUM(amount)"]:
            return apology("less shares available")

        # insert the transaction details into the database
        db.execute("INSERT INTO transactions (user_id, symbol, name, amount, price, current_price, total, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], stock_info["symbol"], stock_info["name"], neg, stock_info["price"], stock_info["price"], total, time)

        # update cash balance
        temp = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        cash_rem = temp[0]["cash"]

        balance = cash_rem - total

        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])

        return redirect("/")

    else:
        return render_template("sell.html", rows=rows)
