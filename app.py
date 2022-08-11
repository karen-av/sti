import datetime
from cs50 import SQL
import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

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
#if not os.environ.get("API_KEY"):
 #   raise RuntimeError("API_KEY not set")


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
    #if session["user_status"] == "admin":
        # передаем данные
        # на всех путях проверять session[user_status]б чтобы не прошли просто по ссылке
     #   return render_template("index")

    #if session["user_status"] == "manager":

    #if session["user_status"] == "couch":

    #

    # user's balance
    cash = db.execute('SELECT * FROM users WHERE id = ?', session['user_id'])[0]['cash'] 
    # user's portfolio
    paper = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session["user_id"]) 
    
    # value user's portfolio
    total = 0
    
    listOfPapers = []
   
   

    return render_template("index.html")


        # create table portfolio (id INTEGER NOT NULL, user_id INTEGER NOT NULL, symbol_prt TEXT NOT NULL, name_prt TEXT, shares_prt INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));
        # create table history (id INTEGER NOT NULL, user_id_hst INTEGER NOT NULL, symbol_hst TEXT NOT NULL, name_hst TEXT, shares_hst INTEGER NOT NULL, price_hst INTEGER NOT NULL, date TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id_hst) REFERENCES users(id));

 

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
        session["user_name"] = rows[0]["username"]


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




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")        
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or checkUsername(username):
            return apology("Invalid username", 403)
        if not username or checkUsernameMastContain(username):
            return apology("Usename not contain symbol from alphabet")
        if  not password or checkPassword(password):
            return apology("Invalid password", 403)
        if not password or checkPasswordBadSymbol(password):
            return apology("Invalid password 2", 403)
        if  not confirmation or password != confirmation:
            return apology("Invalid confirmation", 403)
        
        # Проверка на существование пользователя
        us = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(us) != 0:
            return apology("User exist", 400)

        # Добавляем пользователя и хеш пароля в бд
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password, "pbkdf2:sha256"))
        
        # Remember which user has logged in
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
        session["user_name"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["username"]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


#function check password
def checkPassword(passw):
    symbols = ['!', '@', '#', '$', '%', '&', '?', '-', '+', '=', '~']
    if len(passw) < 6 or len(passw) > 30:
        return True

    a, b, c, d = 0, 0, 0, 0
    for s in passw:
        if s in symbols:
            a = a+1
        if s.isdigit():
            b = b+1
        if s.isupper():
            c = c+1
        if s.islower():
            d = d+1
        if a > 0 and b > 0 and c > 0 and d > 0:
            print(a, b, c, d)
            return False
    print(a, b, c, d)
    return True

def checkPasswordBadSymbol(passw):
    symbols = ['!', '@', '#', '$', '%', '&', '?', '-', '+', '=', '~']
    for p in passw:
        if p not in symbols and not p.isdigit() and not p.isupper() and not p.islower():
            return True
    return False
    
# functionc check username
def checkUsername(name):
    if len(name) < 3 or len(name) > 30:
        return True

    symbols = ['@', '$', '&','-'];
    for n in name:
        if not n.isalpha() and not n.isdigit() and not n in symbols:
            return True
    return False

def checkUsernameMastContain(name):
    for n in name:
        if n.isalpha():
            return False
    return True
