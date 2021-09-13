import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
#from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd, validate

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
session(app)

# Configure CS50 Library to use SQLite database
db = sqlite3.connect("finance.db")
db.row_factory = sqlite3.Row

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    assets = db.execute("SELECT * FROM assets WHERE userID=?", session["user_id"])

    for i in assets:
        realtime = lookup(i["symbol"])
        db.execute("UPDATE assets SET holding_value=? WHERE symbol=?", round(assets[0]["shares"]*realtime["price"], 2), i["symbol"])

    assets = db.execute("SELECT * FROM assets WHERE userID=?", session["user_id"])
    user =  db.execute("SELECT * FROM users WHERE id=?", session["user_id"])
    cash = [i["holding_value"] for i in assets]
    liquidity = usd(user[0]["cash"])
    total_cash = usd(sum(cash)+user[0]["cash"])

    return render_template("index.html", assets=assets, user=user, liquidity = liquidity, total_cash = total_cash, fun = usd)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":

        return render_template("buy.html")

    else:
        stock = lookup(request.form.get("symbol"))
        no_of_shares = request.form.get("shares")
        user = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

        if "." in no_of_shares:
            if int(float(no_of_shares)) != float(no_of_shares):
                return apology("Number of shares must be positive Integer")



        try:
            int(float(no_of_shares))

        except:
            return apology("Number of shares must be positive Integer")

        if stock == None:
            return apology("Invalid Symbol")

        elif int(float(no_of_shares)) <= 0:
            return apology("Number of shares must be positive Integer")

        elif user[0]["cash"] < int(no_of_shares)*stock["price"]:
            return render_template("nobalance.html", curr_balance=usd(user[0]["cash"]), stock_cost=usd(int(no_of_shares)*stock["price"]))

        else:
            db.execute("INSERT INTO payments (userID, symbol, shares, date, cost, transaction_method, balance_before, balance_after) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], stock["symbol"], int(no_of_shares), str(datetime.now())[:19], round(int(no_of_shares)*stock["price"], 2), "buy", round(user[0]["cash"], 2), round(user[0]["cash"] - int(no_of_shares)*stock["price"], 2))
            db.execute("UPDATE users SET cash=? WHERE id=?", user[0]["cash"] - int(no_of_shares)*stock["price"], session["user_id"])
            if len(db.execute("SELECT * FROM assets WHERE userID=? AND companyName=?", session["user_id"], stock["name"])) == 0:
                    db.execute("INSERT INTO assets (userID, symbol, companyName, shares, holding_value) VALUES (?, ?, ?, ?, ?)", session["user_id"], stock["symbol"], stock["name"], int(no_of_shares), int(no_of_shares)*stock["price"])
            else:
                curr_asset = db.execute("SELECT * FROM assets WHERE userID=? AND companyName=?", session["user_id"], stock["name"])
                db.execute("UPDATE assets SET shares=?, holding_value=? WHERE userID=? AND companyName=?", int(no_of_shares)+curr_asset[0]["shares"], (int(no_of_shares)+curr_asset[0]["shares"])*stock["price"], session["user_id"], stock["name"])
            return render_template("buyed.html", curr_balance=usd(user[0]["cash"] - int(no_of_shares)*stock["price"]))


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    payments = db.execute("SELECT * FROM payments WHERE userID=?", session["user_id"])
    payments.reverse()
    return render_template("history.html", history=payments)


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
        stock = lookup(request.form.get("symbol"))

        if stock == None:
            return apology("Invalid Symbol")

        else:
            return render_template("quoted.html", share=stock, usd=usd(stock["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        #check for posted data from user
        if not request.form.get("username"):
            return apology("You Must Provide a username")

        elif not request.form.get("password"):
            return apology("You Must Provide a password")

        elif not request.form.get("confirmation"):
            return apology("You Must Confirm your password")

        elif request.form.get("username") in [i["username"] for i in db.execute("SELECT username FROM users")]:
            return apology("username already exist")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password confirmation does not equal to original password")

        #elif len(request.form.get("password")) < 8 or len(request.form.get("password")) > 12 or not validate(request.form.get("password")):
            #return apology("password must be 8-12 characters (digits and alphabetical characters Only)")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "GET":
        asset = db.execute("SELECT * FROM assets WHERE userID=?", session["user_id"])
        return render_template("sell.html", assets = asset)

    else:
        user =  db.execute("SELECT * FROM users WHERE id=?", session["user_id"])
        asset = db.execute("SELECT * FROM assets WHERE userID=? AND companyName=?", session["user_id"], request.form.get("companyname"))

        if asset[0]["shares"] < int(request.form.get("shares")):
            return render_template("no stocks.html", companyname=request.form.get("companyname"))

        else:
            stock = lookup(asset[0]["symbol"])
            shares = request.form.get("shares")

            db.execute("INSERT INTO payments (userID, symbol, shares, date, cost, transaction_method, balance_before, balance_after) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], asset[0]["symbol"], int(shares), str(datetime.now())[:19], round(stock["price"]*int(shares), 2), "sell", round(user[0]["cash"], 2), round(user[0]["cash"] + (stock["price"]*int(shares)), 2))
            db.execute("UPDATE users SET cash=? WHERE id=?", user[0]["cash"] + (stock["price"]*int(shares)), session["user_id"])
            db.execute("UPDATE assets SET shares=?, holding_value=? WHERE userID=? AND symbol=?", asset[0]["shares"]-int(shares), (asset[0]["shares"]-int(shares))*stock["price"], session["user_id"], asset[0]["symbol"])
            db.execute("DELETE FROM assets WHERE shares=0")
            return render_template("Selled.html",curr_balance=usd(user[0]["cash"] + (stock["price"]*int(shares))))



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
