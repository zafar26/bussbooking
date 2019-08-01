from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bus.db")



@app.route("/")
def index():
    """Handle requests for / via GET (and POST)"""
    data = db.execute("SELECT * FROM busstiming")
    return render_template("index.html",data=data)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return "passwords do not match"

        # hash the password and insert a new user in the database
        hash = generate_password_hash(request.form.get("password"))
        new_user_id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)

        # unique username constraint violated?
        if not new_user_id:
            return "username taken"
      # Remember which user has logged in
        session["user_id"] = new_user_id

        # Display a flash message
        flash("Registered!")
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    """Handle requests for /compare via P"""
    if request.method == "POST":
        flash("searching")
        data = db.execute("SELECT * FROM busstiming WHERE depart=:source and arrived=:destination", source = request.form.get("source"), destination =request.form.get("destination"))

        return render_template("search.html", data=data)
    else:
        return redirect("/")


@app.route("/seatselection", methods=["GET","POST"])
@login_required
def seatselection():
    if request.method =="POST":
        #
        checkboxes = request.form.getlist("seats")
        for checkbox in checkboxes:
            db.execute("INSERT INTO reservedseat (busno, busname, seatno, passengername, age, gender) VALUES(111, 'knr-hyd', :seatno, 'zafar', 21, 'male')",seatno=checkbox)
            return render_template("confirmbooked.html")
        #
    else:
        selectedseat = db.execute("SELECT seatno FROM reservedseat")
        return render_template("seatselection.html", selectedseat=selectedseat)


@app.route("/passengerdetails", methods=["GET","POST"])
def passengerdetails():
    if request.method == "POST":
        return render_template("index.html")
    else:
        return render_template("passengerdetails.html")


@app.route("/buses", methods=["GET", "POST"])
def buses():

    return render_template("index.html")


@app.route("/track", methods=["GET", "POST"])
def track():

    return render_template("index.html")


@app.errorhandler(HTTPException)
def errorhandler(error):
    """Handle errors"""
    return render_template("error.html", error=error)


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
