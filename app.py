
from crypt import methods
from cs50 import SQL
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
db = SQL("sqlite:///sti.db")

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
    if session["user_status"] == "admin":
        users = db.execute("SELECT * FROM users")
        # на всех путях проверять session[user_status]б чтобы не прошли просто по ссылке
        return render_template("admin.html", users = users)
     

    elif session["user_status"] == "manager":
        return render_template("index.html")

    else:
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
        #if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        if len(rows) != 1 or not request.form.get("password") in rows[0]["hash"]:
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]
        session["user_status"] = rows[0]["status"]


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


@app.route("/edit", methods = ["POST"])
@login_required
def edit():
    if request.method == "POST" and session["user_status"] == "admin":
        userId = request.form.get("user_id")
        
        userData = db.execute("SELECT * FROM users WHERE id = ?", userId)
       
        id = userData[0]['id']
        name = userData[0]['name']
        username = userData[0]['username']
        password = userData[0]['hash']
        status  = userData[0]['status']
        position = userData[0]['position']
        return render_template("edit.html", id = id, name= name, username = username, password = password, status = status, position = position)
    else:
        return redirect("/")

@app.route("/editSave", methods = ["POST"])
@login_required
def editSave():
    if request.method == "POST" and session["user_status"] == "admin":
        id = request.form.get("id")
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        status  = request.form.get("status")
        position = request.form.get("position") 

        db.execute("UPDATE users SET name = ?, username = ?, hash = ?, status = ?, position = ?  WHERE id = ?", name, username, password, status, position, id)
        return redirect("/")
    else:
        return redirect("/")


@app.route("/delete", methods = ["POST"])
@login_required
def delete():
    if request.method == "POST" and session["user_status"] == "admin":
        id = request.form.get("id")
        db.execute("DELETE FROM users WHERE id = ?", id)
        return redirect("/")
    else:
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST" and session["user_status"] == "admin":
        name = request.form.get("name")
        username = request.form.get("username")        
        password = request.form.get("password")
        status = request.form.get("status")
        position = request.form.get("position")
       
        if not name:
            return apology("Invalid name", 403)
        if not username or checkUsername(username):
            return apology("Invalid username", 403)
        if checkUsernameMastContain(username):
            return apology("Usename not contain symbol from alphabet")
        if  not password or checkPassword(password):
            return apology("Invalid password", 403)
        if not password or checkPasswordBadSymbol(password):
            return apology("Invalid password 2", 403)
        
        
        # Проверка на существование пользователя
        us = db.execute("SELECT username FROM users WHERE username = ?", username.lower())
        if len(us) != 0:
            return apology("User exist", 400)

        # Добавляем пользователя и хеш пароля в бд
        #hash = generate_password_hash(password, "pbkdf2:sha256")
        hash = password
        db.execute("INSERT INTO users (name, username, hash, status, position) VALUES(?, ?, ?, ?, ?)", name, username, hash, status, position)
        
        # Remember which user has logged in
       # session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
       # session["user_name"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["username"]
       # session['user_status'] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["status"]
        # Redirect user to home page
        return redirect("/")
    else:
        return redirect("/")


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
            
            return False
    
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

    symbols = ['@', '$', '&','-', '_'];
    for n in name:
        if not n.isalpha() and not n.isdigit() and not n in symbols:
            return True
    return False

def checkUsernameMastContain(name):
    for n in name:
        if n.isalpha():
            return False
    return True
