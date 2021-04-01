import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")



############################
##                        ##
##         sql cmd        ##
##                        ##
############################

# CREATE TABLE history (
# transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# symbol TEXT NOT NULL,
# quote INTEGER NOT NULL,
# shares INTEGER NOT NULL,
# total INTEGER NOT NULL,
# time DATETIME NOT NULL,
# u_id INTEGER NOT NULL,
# FOREIGN KEY(u_id) REFERENCES users(id));

### ENTER IN finance.db IN ONE LINE
# CREATE TABLE history (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, symbol TEXT NOT NULL, quote INTEGER NOT NULL, shares INTEGER NOT NULL, total INTEGER NOT NULL, time DATETIME NOT NULL, u_id INTEGER NOT NULL, FOREIGN KEY(u_id) REFERENCES users(id));

### RENAME JUST IN CASE
# ALTER TABLE hitsory
# RENAME TO history

### RESULT
    # CREATE TABLE users (
        # id INTEGER,
        # username TEXT NOT NULL,
        # hash TEXT NOT NULL,
        # cash NUMERIC NOT NULL DEFAULT 10000.00,
        # PRIMARY KEY(id)
        # );
    # CREATE TABLE history (
        # transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        # symbol TEXT NOT NULL,
        # quote INTEGER NOT NULL,
        # shares INTEGER NOT NULL,
        # total INTEGER NOT NULL,
        # time DATETIME NOT NULL,
        # u_id INTEGER NOT NULL,
        # FOREIGN KEY(u_id) REFERENCES users(id)
        # );
    # CREATE UNIQUE INDEX username ON users (username);
    # CREATE TABLE sqlite_sequence(name,seq);


############################
##                        ##
##         Index          ##
##                        ##
############################

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")


############################
##                        ##
##          Buy           ##
##                        ##
############################

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        return render_template("buy.html")

    # if request.method == "POST":

    # return apology("TODO")


############################
##                        ##
##        History         ##
##                        ##
############################

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

# transaction_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# symbol TEXT NOT NULL,
# quote INTEGER NOT NULL,
# shares INTEGER NOT NULL,
# total INTEGER NOT NULL,
# time DATETIME NOT NULL,
# u_id INTEGER NOT NULL,
# FOREIGN KEY(u_id) REFERENCES users(id));

    history = db.execute("SELECT symbol AS Symbol, shares AS Shares, quote AS Quote, time AS Time FROM history WHERE u_id = (?)", session['user_id'])

    return render_template("history.html", history=history)


############################
##                        ##
##          login         ##
##  (distribution code)   ##
##                        ##
############################

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

############################
##                        ##
##         logout         ##
##  (distribution code)   ##
##                        ##
############################

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


############################
##                        ##
##         quote          ##
##                        ##
############################

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    ### Specification
    ### When a user visits /quote via GET
        # render one of those templates,
        # inside of which should be an HTML form that submits to /quote via POST.

    if request.method == "GET":
        return render_template("quote.html")

    ### In response to a POST
        # quote can render that second template,
        # embedding within it one or more values from lookup.

    if request.method == "POST":
        stock = lookup(request.form.get("symbol"))
        if stock == None:
            return apology("invalid symbol")
        else:
            # how lookup('symbol') works:
                # pass in a symbol (e.g., NFLX)
                # returns a dict containing 3 keys:
                # name, whose value is a str
                # price, whose value is a float
                # symbol, whose value is a str
            name = stock.get("name")
            quote = stock.get("price")
            symbol = stock.get("symbol")
            return render_template("quoted.html", name=name, quote=usd(quote), symbol=symbol)

    # return apology("TODO")


############################
##                        ##
##        register        ##
##                        ##
############################

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("no username")
        elif not request.form.get("password"):
            return apology("no password")
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password confirmation does not match")
        else:
            if len(db.execute("SELECT * FROM users WHERE username = (?)", request.form.get("username"))) != 0:
                return apology("username already taken")
            else:
                username = request.form.get("username")
                password = request.form.get("password")
                password_hash = generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)

                rows = db.execute("SELECT * FROM users WHERE username = (?)", username)
                session["user_id"] = rows[0]["id"]

                flash("Registered successfully!")
                return redirect("/")

    return render_template("register.html")


############################
##                        ##
##          Sell          ##
##                        ##
############################

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


############################
##                        ##
##  (distribution code)   ##
##                        ##
############################
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)