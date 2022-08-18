from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from config import host, user, password, db_name
from helpers import apology, login_required, createPassword, checkPassword, checkPasswordBadSymbol, checkUsername, checkUsernameMastContain
import os
from werkzeug.utils import secure_filename
import csv
import pandas as pd
#from flask_sqlalchemy import SQLAlchemy


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

POSITIONS_LIST = ("Директор", "Юрист", "Повар", "Садовник", 'Слесарь', 'DEV', 'Тренер')
STATUS_LIST = ('admin', 'coach', 'manager', 'head')
UPLOAD_FOLDER = 'upload_files'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
ADMIN = 'admin'
COACH = 'coach'
HEAD = 'head'
COMPETENCE  = ('Организованноть', 'Стремление к совершенству', 'Надежность', 'Приверженность', 'Командность', 'Ориентация на клиента', 'Эффективная коммуникация', 'Принятие решений', 'Управленческое мастерство')
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
@login_required
def index():
    if session["user_status"] == ADMIN or session["user_status"] == COACH:
        return render_template('index.html')
    elif session["user_status"] == HEAD:
        return redirect("/users")
    else:
        return redirect("/login")

@app.route("/positions")
@login_required
def positions():
    if session["user_status"] == ADMIN or session["user_status"] == COACH:
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM positions ORDER BY id")
                positions = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return render_template('positions.html', positions = positions, competence = COMPETENCE)
    
    else:
        return redirect("/")


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "GET":
        if session["user_status"] == ADMIN or session["user_status"] == COACH:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users ORDER BY id;")
                    users = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT department FROM users;")
                    usereDepartment = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT reports_to FROM users;")
                    usereReports_to = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT status FROM users;")
                    usereStatus_to = cursor.fetchall()            
                    cursor.execute("SELECT DISTINCT position FROM users UNIC;")
                    userePosition = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT name FROM users;")
                    usereName = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT mail FROM users;")
                    usereMail = cursor.fetchall()
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")

            return render_template("users.html", users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, usereName =usereName, usereMail = usereMail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)

        elif session["user_status"] == HEAD:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM users WHERE mail = %(mail)s", {'mail': session["user_mail"]})
                    headName = cursor.fetchone()
                    cursor.execute("SELECT * FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) AND reports_pos = %(name)s LIMIT 1", {'name': headName[0]})
                    positionFromList = cursor.fetchall()
                    print(f' positionFromList - {positionFromList}')
                    if len(positionFromList) != 0:
                        return render_template("for_head.html", positionFromList = positionFromList, competence = COMPETENCE)
                    else:
                        return render_template('theEnd.html')
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
        
        else:
            return redirect("/")


    elif request.method == "POST":
        if session["user_status"] == ADMIN or session["user_status"] == COACH:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT department FROM users;")
                    usereDepartment = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT reports_to FROM users;")
                    usereReports_to = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT status FROM users;")
                    usereStatus_to = cursor.fetchall()            
                    cursor.execute("SELECT DISTINCT position FROM users UNIC;")
                    userePosition = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT name FROM users;")
                    usereName = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT mail FROM users;")
                    usereMail = cursor.fetchall()

                    department = request.form.get("department")
                    reports_to = request.form.get("reports_to")
                    status = request.form.get("status")
                    position  = request.form.get("position")
                    #name = request.form.get("name")
                    #mail = request.form.get("mail").lower()
                    if not department and not reports_to and not status and not position:
                        cursor.execute("SELECT * FROM users ORDER BY id;")
                        users = cursor.fetchall()

                    elif not reports_to and not status and not position:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s ORDER BY id", {'department': department})
                        users = cursor.fetchall()
                        #cursor.execute("SELECT DISTINCT department FROM users WHERE department = %(department)s", {'department': department})
                        #usereDepartment = cursor.fetchall()
                    elif not department and not status and not position:
                        cursor.execute("SELECT * FROM users WHERE reports_to = %(reports_to)s ORDER BY id", {'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif not reports_to and not department and not position:
                        cursor.execute("SELECT * FROM users WHERE status = %(status)s ORDER BY id", {'status': status})
                        users = cursor.fetchall()
                    elif not reports_to and not department and not status:
                        cursor.execute("SELECT * FROM users WHERE position = %(position)s ORDER BY id", {'position': position})
                        users = cursor.fetchall()

                    elif not status and not position:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and reports_to = %(reports_to)s ORDER BY id", {'department': department, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif not department and not position:
                        cursor.execute("SELECT * FROM users WHERE reports_to = %(reports_to)s and status = %(status)s ORDER BY id", {'reports_to': reports_to, 'status': status})
                        users = cursor.fetchall()
                    elif not reports_to and not position:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and status = %(status)s ORDER BY id", {'department': department, 'status': status})
                        users = cursor.fetchall()
                    elif not department and not status:
                        cursor.execute("SELECT * FROM users WHERE position = %(position)s and reports_to = %(reports_to)s ORDER BY id", {'position': position, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif not department and not reports_to:
                        cursor.execute("SELECT * FROM users WHERE status = %(status)s and position = %(position)s ORDER BY id", {'status': status, 'position': position})
                        users = cursor.fetchall()
                    elif not reports_to and not status:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and position = %(position)s ORDER BY id", {'department': department, 'position': position})
                        users = cursor.fetchall()
                    
                    elif not reports_to:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and status = %(status)s and position = %(position)s ORDER BY id", {'department': department, 'status': status, 'position':position})
                        users = cursor.fetchall()
                    elif not department:
                        cursor.execute("SELECT * FROM users WHERE position = %(position)s and reports_to = %(reports_to)s and status = %(status)s ORDER BY id", {'position': position, 'reports_to': reports_to, 'status': status})
                        users = cursor.fetchall()
                    elif not status:
                        cursor.execute("SELECT * FROM users WHERE reports_to = %(reports_to)s and position = %(position)s and %(department)s ORDER BY id", {'reports_to': reports_to, 'position': position, 'department': department})
                        users = cursor.fetchall()
                    elif not position:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and reports_to = %(reports_to)s AND status = %(status)s ORDER BY id", {'department': department, 'status': status, 'reports_to': reports_to})
                        users = cursor.fetchall()

                    else:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s and reports_to = %(reports_to)s and status = %(status)s and position = %(position)s ORDER BY id", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position})
                        users = cursor.fetchall()

                    #cursor.execute("SELECT * FROM users WHERE department = %(department)s and reports_to = %(reports_to)s and status = %(status)s and position = %(position)s and name = %(name)s and mail = %(mail)s ORDER BY id", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail})
                    

            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
            # на всех путях проверять session[user_status]б чтобы не прошли просто по ссылке
            return render_template("select.html", users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, usereName =usereName, usereMail = usereMail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
        
        elif session["user_status"] == HEAD:
            position_pos = request.form.get('position_pos')
            comp_1 = request.form.get('comp_1')
            comp_2 = request.form.get('comp_2')
            comp_3 = request.form.get('comp_3')
            comp_4 = request.form.get('comp_4')
            comp_5 = request.form.get('comp_5')
            comp_6 = request.form.get('comp_6')
            comp_7 = request.form.get('comp_7')
            comp_8 = request.form.get('comp_8')
            comp_9 = request.form.get('comp_9')

            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    # Вносим полученные данные
                    cursor.execute("UPDATE positions SET comp_1 = %(comp_1)s, comp_2 = %(comp_2)s, comp_3 = %(comp_3)s, comp_4 = %(comp_4)s, comp_5 = %(comp_5)s, comp_6 = %(comp_6)s, comp_7 = %(comp_7)s, comp_8 = %(comp_8)s, comp_9 = %(comp_9)s WHERE position_pos = %(position_pos)s", {'comp_1': comp_1, 'comp_2':comp_2, 'comp_3': comp_3, 'comp_4': comp_4, 'comp_5': comp_5, 'comp_6': comp_6, 'comp_7': comp_7, 'comp_8':comp_8, 'comp_9': comp_9, 'position_pos': position_pos})
                    # Находим имя руководителя
                    cursor.execute("SELECT name FROM users WHERE mail = %(mail)s", {'mail': session["user_mail"]})
                    headName = cursor.fetchone()
                    # Находим неранжированную должность
                    cursor.execute("SELECT * FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) AND reports_pos = %(name)s LIMIT 1", {'name': headName[0]})
                    positionFromList = cursor.fetchall()
                    # Если есть такая должность, то передаем ее для заполнения
                    if len(positionFromList) != 0:
                        return render_template("for_head.html", positionFromList = positionFromList, competence = COMPETENCE)
                    # Если нет, то прощаемся 
                    else:
                        return render_template('theEnd.html')
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")

        else:
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("mail"):
            flash('Вы не указали логин')
            return render_template('/login.html' )
            #return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("hash"):
            flash('Вы не указали пароль')
            return render_template('/login.html' )
            #return apology("must provide password", 403)

        # Query database for username
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                mail = request.form.get('mail').lower().strip()
                cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                rows = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        # Ensure username exists and password is correct
        
        if len(rows) != 1 or request.form.get("hash") != rows[0][7]:
            flash('Вы указали неверный логин или пароль')
            return render_template('/login.html' )
            #return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["user_name"] = rows[0][5]
        session["user_status"] = rows[0][3]
        session["user_mail"] = rows[0][6]


        # Redirect user to home page
        return redirect('/' )

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
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        userId = request.form.get("user_id")
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %(userId)s", {'userId': userId})
                userData = cursor.fetchall()

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
  
        id = userData[0][0]
        department = userData[0][1]
        reports_to = userData[0][2]
        status = userData[0][3]
        position = userData[0][4]
        name = userData[0][5]
        mail = userData[0][6]
        hash = userData[0][7]

        
        return render_template("edit.html", id = id, department = department, reports_to = reports_to, status = status, position = position, name = name, mail = mail, hash = hash, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
    else:
        return redirect("/")


@app.route("/editSave", methods = ["POST"])
@login_required
def editSave():
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        id = request.form.get("id")
        department = request.form.get("department")
        reports_to = request.form.get("reports_to")
        status = request.form.get("status")
        position  = request.form.get("position")
        name = request.form.get("name")
        mail = request.form.get("mail").lower().strip()
        hash = request.form.get("hash")
        if not status or not position or status == 'None' or position == 'None':
            flash('Изменения не сохранены. Укажите статус и должность.')
            return redirect('/users')
        if not name:
            flash('Изменения не сохранены. Укажите правильный формат имени')
            return redirect('/users')
        if not mail or checkUsername(mail):
            flash('Изменения не сохранены. Укажите правильный формат почты')
            return redirect('/users')
        if checkUsernameMastContain(mail):
            flash('Изменения не сохранены. Укажите правильный формат почты')
            return redirect('/users')
        if  (status == ADMIN or status == COACH or status == HEAD) and (not hash or checkPassword(hash)):
            flash('Изменения не сохранены. Укажите правильный формат пароля')
            return redirect('/users')
        if (status == ADMIN or status == COACH or status == HEAD) and (not hash or checkPasswordBadSymbol(hash)):
            flash('Изменения не сохранены. Укажите правильный формат пароля')
            return redirect('/users')
        

        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                # Проверка на существование пользователя
                cursor.execute("SELECT mail FROM users WHERE mail = %(mail)s AND id != %(id)s", {'mail': mail, 'id': id})
                us = cursor.fetchall()         
                if len(us) != 0 :
                    return apology("User exist", 400)
                # внесение изменений
                cursor.execute("UPDATE users SET department = %(department)s, reports_to = %(reports_to)s, status = %(status)s, position = %(position)s, name = %(name)s, mail = %(mail)s, hash = %(hash)s  WHERE id = %(id)s", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash, 'id': id})
                # Если изменили должность и такой нет в базе, добавляем

                # Проверяем существует ли должность в базе. Если нет, то добавляем
                cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s", {'position': position})
                pos = cursor.fetchall()
                if len(pos) == 0 and status != ADMIN and status != COACH:
                    cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})


        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        
        flash('Изменения сохранены.')
        return redirect("/users")
    else:
        return redirect("/")


@app.route("/delete", methods = ["POST"])
@login_required
def delete():
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        id = request.form.get("id")

        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %(id)s", {'id': id})

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        flash('Пользователь удален.')
        return redirect("/users")
    else:
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        department = request.form.get("department")
        reports_to = request.form.get("reports_to")
        status = request.form.get("status")
        position  = request.form.get("position")
        name = request.form.get("name").strip()
        mail = request.form.get("mail").lower().strip()
        hash = ''

        # Проверка полученных данных
        if not status or not position:
            flash('Укажите должность и статус')
            return redirect('/users')
        if not name:
            flash('Укажите Имя')
            return redirect('/users')
            #return apology("Invalid name", 403)
        if not mail or checkUsername(mail):
            flash('Укажите почту')
            return redirect('/users')
            #return apology("Invalid username", 403)
        if checkUsernameMastContain(mail):
            flash('Укажите почту')
            return redirect('/users')
            #return apology("Usename not contain symbol from alphabet")
            # Если пользователь со статусом ... создаем пароль
        if  status == ADMIN or status == COACH or status == HEAD: # and (not hash or checkPassword(hash)):
            hash = createPassword()
          
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                
                # Проверка на существование пользователя
                cursor.execute("SELECT mail FROM users WHERE mail = %(mail)s", {'mail': mail})
                us = cursor.fetchall()
                if len(us) != 0:
                    flash('Электронная почта уже зарегистрирована')
                    return redirect('/users')
                cursor.execute("INSERT INTO users (department, reports_to, status, position, name, mail, hash) VALUES(%(department)s, %(reports_to)s, %(status)s, %(position)s, %(name)s, %(mail)s, %(hash)s)", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash})
                
                # Проверяем существует ли должность в базе. Если нет, то добавляем
                cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s", {'position': position})
                pos = cursor.fetchall()
                if len(pos) == 0 and status != ADMIN and status != COACH:
                    cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        flash('Пользователь добавлен.')
        return redirect("/users")
    else:
        return redirect("/")


@app.route("/file", methods=["POST"])
@login_required
def file():
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        if not request.files['file']:
            flash('Не могу прочитать файл или файл не загружен')
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            flash('Не могу прочитать файл')
            return redirect('/')
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        countError = 0
        countUpload = 0
        usersError = []
        usersUpload = []
           
        if filename.endswith((".xlsx", ".xls")):
            xlsx = pd.ExcelFile(f'upload_files/{filename}')
            table = xlsx.parse()
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True 
                with connection.cursor() as cursor:
                    for i in range(len(table)):
                        # Разбираем данные из считанных строк
                        department = str(table.iloc[i,:][0])
                        reports_to = str(table.iloc[i,:][1])
                        status = str(table.iloc[i,:][2])
                        position = str(table.iloc[i,:][3])
                        name = str(table.iloc[i,:][4]).strip()
                        mail = str(table.iloc[i,:][5]).lower().strip()
                        hash = ''
                        # если статус ... устанавливаем рандомный пароль
                        if status == COACH or status == ADMIN or status == HEAD:
                            hash = createPassword()
                        # проверить пользователя на сущесвование
                        cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                        us = cursor.fetchall()
                        # Если сузествует, то не записываем в базу. Добавляем в список
                        if len(us) != 0:
                            countError = countError + 1
                            usersError = usersError + us
                        # Если нет пользователя в базе, то записываем туда и добавляем в список
                        else:
                            cursor.execute("INSERT INTO users (department, reports_to, status, position, name, mail, hash) VALUES(%(department)s, %(reports_to)s, %(status)s, %(position)s, %(name)s, %(mail)s, %(hash)s)", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash})
                            countUpload = countUpload + 1
                            cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                            usUpload = cursor.fetchall()
                            usersUpload = usersUpload + usUpload
                            # Проверяем должность в базе. Если существует, то пропускам
                            cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s", {'position': position})
                            pos = cursor.fetchall()
                            if len(pos) == 0 and status != ADMIN and status != COACH:
                                cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})


            except Exception as _ex:
                    print("[INFO] Error while working with PostgresSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")  
                    
        elif filename.endswith(".csv"):
            with open(f'upload_files/{filename}', newline="") as csvfile:
                userData = csv.reader(csvfile, delimiter=';', quotechar='|')
                next(userData)
                try:
                    connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                    connection.autocommit = True  
                    
                    with connection.cursor() as cursor:
                        print(userData)
                        for userD in userData:
                            department = userD[0]
                            reports_to = userD[1]
                            status = userD[2]
                            position = userD[3]
                            name = userD[4]
                            mail = userD[5]         
                            hash = ''
                            if status == 'coach' or status == HEAD:
                                hash = createPassword()
                            # проверить пользователя на сущесвование
                            cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                            us = cursor.fetchall()

                            if len(us) != 0:
                                countError = countError + 1
                                usersError = usersError + us
                            else:
                                cursor.execute("INSERT INTO users (department, reports_to, status, position, name, mail, hash) VALUES(%(department)s, %(reports_to)s, %(status)s, %(position)s, %(name)s, %(mail)s, %(hash)s)", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash})
                                countUpload = countUpload + 1
                                cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                                usUpload = cursor.fetchall()
                                usersUpload = usersUpload + usUpload
                                cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s", {'position': position})
                                pos = cursor.fetchall()
                                if len(pos) == 0 and status != ADMIN and status != COACH:
                                    cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})



                except Exception as _ex:
                    print("[INFO] Error while working with PostgresSQL", _ex)
                finally:
                    if connection:
                        connection.close()
                        print("[INFO] PostgresSQL connection closed")                  

        else:
            flash('Тип загруженного файла не поддерживается.')
            return redirect('/')
        return render_template('afterUpload.html', countError = countError, countUpload = countUpload, usersError = usersError, usersUpload = usersUpload)
    else:
        return redirect('/')


# create table portfolio (id INTEGER NOT NULL, user_id INTEGER NOT NULL, symbol_prt TEXT NOT NULL, name_prt TEXT, shares_prt INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));
# create table history (id INTEGER NOT NULL, user_id_hst INTEGER NOT NULL, symbol_hst TEXT NOT NULL, name_hst TEXT, shares_hst INTEGER NOT NULL, price_hst INTEGER NOT NULL, date TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id_hst) REFERENCES users(id));
# CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, status TEXT, name text, position text);
# CREATE TABLE sqlite_sequence(name,seq);

#CREATE TABLE users (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY NOT NULL, department VARCHAR(50), reports_to VARCHAR(50), status VARCHAR(50), position VARCHAR(50), name VARCHAR(50), mail VARCHAR(50) UNIQUE, hash VARCHAR(50));
# INSERT INTO users (department, reports_to, status, position, name, mail, hash) VALUES('1', 'Юр.Отдел', 'Виктор Иванов' , 'admin' , 'dev', 'Karen', 'asd@asd.ri', 'edrfTgr34=');


#CREATE TABLE positions (ID INTEGER NOT NULL PRIMARY KEY, position_pos VARCHAR(50), reports_pos VARCHAR(50), comp_1 INTEGER, comp_2 INTEGER, comp_3 INTEGER, comp_4 INTEGER, comp_5 INTEGER, comp_6 INTEGER, comp_7 INTEGER, comp_8 INTEGER, comp_9 INTEGER);