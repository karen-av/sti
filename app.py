
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from config import host, user, password, db_name
from helpers import apology, login_required, usd
#from flask_sqlalchemy import SQLAlchemy


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
#db = SQL("sqlite:///sti.db")
POSITIONS_LIST = ("Директор", "Логист", "Повар", "Садовник")
STATUS_LIST = ('admin', 'couch', 'manager', 'BUH' )

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
        #users = db.execute("SELECT * FROM users")
        #users = func_sql("SELECT * FROM users;")
        try:
            # connect to exist database
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            #insert data to table
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users ORDER BY id;")
                users = cursor.fetchall()
                print(users)
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        #print(f"users - {users}")
        # на всех путях проверять session[user_status]б чтобы не прошли просто по ссылке
        return render_template("admin.html", users = users, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
     

    elif session["user_status"] == "manager":
        return render_template("index.html")

    else:
        return render_template("index.html")


        # create table portfolio (id INTEGER NOT NULL, user_id INTEGER NOT NULL, symbol_prt TEXT NOT NULL, name_prt TEXT, shares_prt INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));
        # create table history (id INTEGER NOT NULL, user_id_hst INTEGER NOT NULL, symbol_hst TEXT NOT NULL, name_hst TEXT, shares_hst INTEGER NOT NULL, price_hst INTEGER NOT NULL, date TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id_hst) REFERENCES users(id));
        # CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, status TEXT, name text, position text);
        # CREATE TABLE sqlite_sequence(name,seq);
 

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
        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                username = request.form.get('username')
                cursor.execute("SELECT * FROM users WHERE username = %(username)s", {'username': username})
                rows = cursor.fetchall()
                print(len(rows))
                
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        

        # Ensure username exists and password is correct
        #if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        if len(rows) != 1 or request.form.get("password") != rows[0][3]:
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["user_name"] = rows[0][1]
        session["user_status"] = rows[0][4]


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
        print(userId)
        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %(userId)s", {'userId': userId})
                userData = cursor.fetchall()
                print(userData)
                
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
  
        id = userData[0][0]
        username = userData[0][1]
        name = userData[0][2]
        userPassword = userData[0][3]
        status  = userData[0][4]
        position = userData[0][5]
        return render_template("edit.html", id = id, name= name, username = username, userPassword = userPassword, status = status, position = position, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
    else:
        return redirect("/")

@app.route("/editSave", methods = ["POST"])
@login_required
def editSave():
    if request.method == "POST" and session["user_status"] == "admin":
        id = request.form.get("id")
        name = request.form.get("name")
        username = request.form.get("username").lower()
        userPassword = request.form.get("password")
        status  = request.form.get("status")
        position = request.form.get("position")
        check = 'None'
        print(status) 

        if not name:
            return apology("Invalid name", 403)
        if not username or checkUsername(username):
            return apology("Invalid username", 403)
        if checkUsernameMastContain(username):
            return apology("Usename not contain symbol from alphabet")
        if  not userPassword or checkPassword(userPassword):
            return apology("Invalid password", 403)
        if not userPassword or checkPasswordBadSymbol(userPassword):
            return apology("Invalid password 2", 403)
        if not status or not position or status == check or position == check:
            return apology("Invalid status or position", 403)

        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                # Проверка на существование пользователя
                cursor.execute("SELECT username FROM users WHERE username = %(username)s AND id != %(id)s", {'username': username, 'id': id})
                us = cursor.fetchall()         
                if len(us) != 0 :
                    return apology("User exist", 400)
                # внесение изменений
                cursor.execute("UPDATE users SET name = %(name)s, username = %(username)s, hash = %(hash)s, status = %(status)s, position = %(position)s  WHERE id = %(id)s", {'name': name, 'username': username, 'hash': userPassword, 'status': status, 'position': position, 'id': id})
                
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return redirect("/")
    else:
        return redirect("/")


@app.route("/delete", methods = ["POST"])
@login_required
def delete():
    if request.method == "POST" and session["user_status"] == "admin":
        id = request.form.get("id")

        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %(id)s", {'id': id})

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        
        return redirect("/")
    else:
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST" and session["user_status"] == "admin":
        name = request.form.get("name")
        username = request.form.get("username").lower()        
        userPassword = request.form.get("password")
        status = request.form.get("status")
        position = request.form.get("position")
       
        if not name:
            return apology("Invalid name", 403)
        if not username or checkUsername(username):
            return apology("Invalid username", 403)
        if checkUsernameMastContain(username):
            return apology("Usename not contain symbol from alphabet")
        if  not userPassword or checkPassword(userPassword):
            return apology("Invalid password", 403)
        if not userPassword or checkPasswordBadSymbol(userPassword):
            return apology("Invalid password 2", 403)
        if not status or not position:
            return apology("Invalid status or position", 403)
        
        
        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                
                # Проверка на существование пользователя
                cursor.execute("SELECT username FROM users WHERE username = %(username)s", {'username': username})
                us = cursor.fetchall()
                if len(us) != 0:
                    return apology("User exist", 400)

                # Добавляем пользователя и хеш пароля в бд
                #hash = generate_password_hash(password, "pbkdf2:sha256")
                
                cursor.execute("INSERT INTO users (name, username, hash, status, position) VALUES(%(name)s, %(username)s, %(hash)s, %(status)s, %(position)s)", {'name': name, 'username': username, 'hash': userPassword, 'status': status, 'position': position})
        

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

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
