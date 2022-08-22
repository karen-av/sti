from flask import Flask, redirect, render_template, request, session, flash
from flask_mail import Mail, Message
from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from config import host, user, password, db_name
from helpers import apology, login_required, createPassword, checkPassword, checkPasswordBadSymbol, checkUsername, checkUsernameMastContain
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import csv
import pandas as pd
import datetime
#from flask_sqlalchemy import SQLAlchemy


# Configure application
app = Flask(__name__)


app.config['DEBAG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.hoster.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'sti@a-okko.ru'
app.config['MAIL_PASSWORD'] = 'feEG9e43=r4'
app.config['MAIL_DEFAULT_SENDER'] = 'sti@a-okko.ru'
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)


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
HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ', 'Дисциплинированность', 'Исполнительность', 'Ответственность', 'Решительность', 'ОРГАНИЗОВАННОСТЬ', 'Чёткое целеполагание', 'Адаптивность', 'Планирование', 'Стремление к порядку', 'СТРЕМЛЕНИЕ К СОВЕРШЕНСТВУ', 'Стремление к достижениям', 'Стремление к развитию', 'Инновационность', 'ПРИВЕРЖЕННОСТЬ', 'Лояльность', 'Взаимовыручка', 'КОМАНДНОСТЬ', 'Готовность к компромиссу', 'Сотрудничество', 'Открытость', 'Открытость обратной связи', 'КЛИЕНТООРИЕНТИРОВАННОСТЬ', 'Ориентация на потребности клиента', 'Партнёрство', 'ПРИНЯТИЕ РЕШЕНИЙ', 'Системное мышление', 'Бизнес-мышление', 'Перспективное мышление', 'ЭФФЕКТИВНАЯ КОММУНИКАЦИЯ', 'Чёткая коммуникация', 'Убеждение и влияние', 'Ведение переговоров', 'Кроссфункциональное взаимодействие', 'Неформальное лидерство', 'УПРАВЛЕНЧЕСКОЕ МАСТЕРСТВО', 'Управление исполнением', 'Мотивация подчинённых', 'Организация работы', 'Управление изменениями', 'Развитие подчинённых', 'Управление командой')
#HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ', 'Дисциплинированность', 'Исполнительность', 'Ответственность')
#HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ 1', 'Дисциплинированность 2', 'Исполнительность 3', 'Ответственность 4', 'Решительность5', 'ОРГАНИЗОВАННОСТЬ6', 'Чёткое целеполагание7', 'Адаптивность8', 'Планирование9', 'Стремление к порядку10', 'СТРЕМЛЕНИЕ К СОВЕРШЕНСТВУ11', 'Стремление к достижениям12', 'Стремление к развитию13', 'Инновационность14', 'ПРИВЕРЖЕННОСТЬ15', 'Лояльность16', 'Взаимовыручка17', 'КОМАНДНОСТЬ18', 'Готовность к компромиссу19', 'Сотрудничество20', 'Открытость21', 'Открытость обратной связи22', 'КЛИЕНТООРИЕНТИРОВАННОСТЬ23', 'Ориентация на потребности клиента24', 'Партнёрство25', 'ПРИНЯТИЕ РЕШЕНИЙ26', 'Системное мышление27', 'Бизнес-мышление28', 'Перспективное мышление29', 'ЭФФЕКТИВНАЯ КОММУНИКАЦИЯ30', 'Чёткая коммуникация31', 'Убеждение и влияние32', 'Ведение переговоров33', 'Кроссфункциональное взаимодействие34', 'Неформальное лидерство35', 'УПРАВЛЕНЧЕСКОЕ МАСТЕРСТВО36', 'Управление исполнением37', 'Мотивация подчинённых38', 'Организация работы39', 'Управление изменениями40', 'Развитие подчинённых41', 'Управление командой42')
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
            return render_template("users.html", users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, usereName =usereName, usereMail = usereMail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
        
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
            print(f'comp_1 - {comp_1}')

            if not comp_1 or not comp_2 or not comp_3 or not comp_4 or not comp_5 or not comp_6 or not comp_7 or not comp_8 or not comp_9:
                flash("Пожалуйста, укажите все значения")
                return redirect ("/users")

            if  int(comp_1) > 9 or int(comp_1) < 1 or int(comp_2) > 9 or int(comp_2) < 1 or int(comp_3) > 9 or int(comp_3) < 1 or int(comp_4) > 9 or int(comp_4) < 1 or int(comp_5) > 9 or int(comp_5) < 1 or int(comp_6) > 9 or int(comp_6) < 1 or int(comp_7) > 9 or int(comp_7) < 1 or int(comp_8) > 9 or int(comp_8) < 1 or int(comp_9) > 9 or int(comp_9) < 1:
                flash("Пожалуйста, укажите все значения. Значения должны быть в диапазоне от 1 до 9.")
                return redirect ("/users")

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
           

        # Ensure password was submitted
        elif not request.form.get("hash") or len(request.form.get("hash")) < 3:
            flash('Вы указали неверный пароль')
            return render_template('/login.html' )
            

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
        
        if len(rows) != 1 or not check_password_hash(rows[0][7], request.form.get("hash")):
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
                cursor.execute("SELECT id, department, reports_to, status, position, name, mail FROM users WHERE id = %(userId)s", {'userId': userId})
                userData = cursor.fetchall()
                print(userData)

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
        
        return render_template("edit.html", id = id, department = department, reports_to = reports_to, status = status, position = position, name = name, mail = mail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
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
        if  hash and (status == ADMIN or status == COACH or status == HEAD):
            if checkPassword(hash) or checkPasswordBadSymbol(hash):
                flash('Изменения не сохранены. Укажите правильный формат пароля')
                return redirect('/users')
            hash = generate_password_hash(hash, "pbkdf2:sha256")


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
            hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
            
          
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


@app.route("/file_users", methods=["GET", "POST"])
@login_required
def file():
    if request.method == "GET" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        return render_template('upload_file.html', typeDataFlag = 'users')

    elif request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        
        # Проверяем получен ли файл
        if not request.files['file']:
            flash('Не могу прочитать файл или файл не загружен')
            return redirect('/file_users')
        file = request.files['file']
        # Проверка имени файла
        if file.filename == '':
            flash('Не могу прочитать файл')
            return redirect('/file_users')
        # Безовасное сохраниение имени файла
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Счетскики загруженных пользователей и списи для выводаинформаци о загруженных и незагруженных пользхователях
        countError = 0
        countUpload = 0
        usersError = []
        usersUpload = []
        
        # если расширение файла excel, то разбираем файл посточно
        if filename.endswith((".xlsx", ".xls")):
            xlsx = pd.ExcelFile(f'upload_files/{filename}')
            table = xlsx.parse()
            # Подключаемся к базе данных
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
                            hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
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
                                hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
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
        
        flash(f"Загруженно {countUpload} пользователей. Не загружено {countError} пользователей.")
        return redirect ('/users')
        # не самый красивый вариант
        #return render_template('afterUpload.html', countError = countError, countUpload = countUpload, usersError = usersError, usersUpload = usersUpload)
    
    else:
        return redirect('/')

@app.route('/testResults', methods=['POST', 'GET'])
@login_required
def testResults():
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):

        # подключаемся к базе и передаем на страницу все результатьы тестов пользователей
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management FROM test_results;")
                testResults = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Erroe while working with PostgraseSQL", _ex)
        finally :
            if connection:
                connection.close()
                print("[INFO] PostgraseSQL connection closed")   

        return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST)

    else:
        # МЕТЕД ПОСТ бУДЕТ РЕЗУЛЬТАТ ФЛЬТРА
        return redirect('/')


@app.route('/file_test', methods = ["GET", "POST"])
@login_required
def file_test():
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        return render_template('upload_file.html', typeDataFlag = 'results')

    # Описание есть в загрузке файла с пользователями /file
    elif request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        if not request.files['file']:
            flash('Не могу прочитать файл или файл не загружен')
            return redirect('/file_test')
        file = request.files['file']
        if file.filename == '':
            flash('Не могу прочитать файл')
            return redirect('/file_test')
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
                print(f"[INFO] PosgreseSQL star connectoin.")
                with connection.cursor() as cursor:
                    for i in range(len(table)):
                        mail = str(table.iloc[i,:][2])
                        cursor.execute("SELECT * FROM test_results WHERE mail = %(mail)s", {'mail': mail})
                        user_result = cursor.fetchall()
                        if len(user_result) == 0:
                            reliability = int(table.iloc[i,:][6])
                            discipline = int(table.iloc[i,:][7])
                            executive = int(table.iloc[i,:][8])
                            responsibility = int(table.iloc[i,:][9])
                            resolved = int(table.iloc[i,:][10])
                            organizational = int(table.iloc[i,:][11])
                            software = int(table.iloc[i,:][12])
                            adaptation = int(table.iloc[i,:][13])
                            planning = int(table.iloc[i,:][14])
                            page = int(table.iloc[i,:][15])
                            strengthening = int(table.iloc[i,:][16])
                            building_on_achievements = int(table.iloc[i,:][17])
                            building_for_development = int(table.iloc[i,:][18])
                            innovation = int(table.iloc[i,:][19])
                            approved = int(table.iloc[i,:][20])
                            loyalty = int(table.iloc[i,:][21])
                            currency = int(table.iloc[i,:][22])
                            country = int(table.iloc[i,:][23])
                            preparedness_for_compromise = int(table.iloc[i,:][24])
                            cooperation = int(table.iloc[i,:][25])
                            openness = int(table.iloc[i,:][26])
                            openness_of_feedback = int(table.iloc[i,:][27])
                            clientoority = int(table.iloc[i,:][28])
                            customer_needs_orientation = int(table.iloc[i,:][29])
                            partnership = int(table.iloc[i,:][30])
                            adoption_of_decisions = int(table.iloc[i,:][31])
                            systemic_thinking = int(table.iloc[i,:][32])
                            business = int(table.iloc[i,:][33])
                            forward_thinking = int(table.iloc[i,:][34])
                            effective_communication = int(table.iloc[i,:][35])
                            clean_communication = int(table.iloc[i,:][36])
                            impunity_and_influence = int(table.iloc[i,:][37])
                            negotiations = int(table.iloc[i,:][38])
                            cross_functional_interaction = int(table.iloc[i,:][39])
                            informal_leadership = int(table.iloc[i,:][40])
                            management = int(table.iloc[i,:][41])
                            implementation_management = int(table.iloc[i,:][42])
                            motivation_of_subordinates = int(table.iloc[i,:][43])
                            organization_of_work = int(table.iloc[i,:][44])
                            change_management = int(table.iloc[i,:][45])
                            development_of_subordinates = int(table.iloc[i,:][46])
                            command_management = int(table.iloc[i,:][47])

                            cursor.execute("INSERT INTO test_results (mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management) VALUES (%(mail)s, %(reliability)s, 	%(discipline)s, 	%(executive)s, 	%(responsibility)s, 	%(resolved)s, 	%(organizational)s, 	%(software)s, 	%(adaptation)s, 	%(planning)s, 	%(page)s, 	%(strengthening)s, 	%(building_on_achievements)s, 	%(building_for_development)s, 	%(innovation)s, 	%(approved)s, 	%(loyalty)s, 	%(currency)s, 	%(country)s, 	%(preparedness_for_compromise)s, 	%(cooperation)s, 	%(openness)s, 	%(openness_of_feedback)s, 	%(clientoority)s, 	%(customer_needs_orientation)s, 	%(partnership)s, 	%(adoption_of_decisions)s, 	%(systemic_thinking)s, 	%(business)s, 	%(forward_thinking)s, 	%(effective_communication)s, 	%(clean_communication)s, 	%(impunity_and_influence)s, 	%(negotiations)s, 	%(cross_functional_interaction)s, 	%(informal_leadership)s, 	%(management)s, 	%(implementation_management)s, 	%(motivation_of_subordinates)s, 	%(organization_of_work)s, 	%(change_management)s, 	%(development_of_subordinates)s, 	%(command_management)s)", {'mail': mail, 'reliability': reliability, 	'discipline': discipline, 	'executive': executive, 	'responsibility': responsibility, 	'resolved': resolved, 	'organizational': organizational, 	'software': software, 	'adaptation': adaptation, 	'planning': planning, 	'page': page, 	'strengthening': strengthening, 	'building_on_achievements': building_on_achievements, 	'building_for_development': building_for_development, 	'innovation': innovation, 	'approved': approved, 	'loyalty': loyalty, 	'currency': currency, 	'country': country, 	'preparedness_for_compromise': preparedness_for_compromise, 	'cooperation': cooperation, 	'openness': openness, 	'openness_of_feedback': openness_of_feedback, 	'clientoority': clientoority, 	'customer_needs_orientation': customer_needs_orientation, 	'partnership': partnership, 	'adoption_of_decisions': adoption_of_decisions, 	'systemic_thinking': systemic_thinking, 	'business': business, 	'forward_thinking': forward_thinking, 	'effective_communication': effective_communication, 	'clean_communication': clean_communication, 	'impunity_and_influence': impunity_and_influence, 	'negotiations': negotiations, 	'cross_functional_interaction': cross_functional_interaction, 	'informal_leadership': informal_leadership, 	'management': management, 	'implementation_management': implementation_management, 	'motivation_of_subordinates': motivation_of_subordinates, 	'organization_of_work': organization_of_work, 	'change_management': change_management, 	'development_of_subordinates': development_of_subordinates, 	'command_management': command_management})
                            countUpload = countUpload + 1

                        else: 
                            countError = countError + 1

            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")
            flash(f"Загруженно {countUpload} результатов тестирования. Не загружено {countError} результатов тестирования.")
            return redirect ('/testResults')

    else:
        return redirect ('/')

@app.route('/mail_heads', methods = ['GET', 'POST'])
@login_required
def mail_heads():
    if request.method == 'GET':
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                status = HEAD
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':status})
                users = cursor.fetchall()
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")

        return render_template('mail.html', users = users)

    else:
        user_mail = request.form.get('user_mail')
        if not user_mail:
            pass
            flash("Не указана электронная почта получателя приглашения")

        today = datetime.date.today()
        user_password = createPassword()
        hash = generate_password_hash(user_password, "pbkdf2:sha256")
        msg = Message('Hey There!', recipients=[user_mail])
        msg.body = (f'Welcom to 123.com.\nYour login {user_mail}\nYour password {user_password}')
        mail.send(msg)

        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                users = cursor.fetchall()
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")

        flash('Приглашение отправлено.')
        return redirect('/mail_heads')

#CREATE TABLE users (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY NOT NULL, department VARCHAR(50), reports_to VARCHAR(50), status VARCHAR(50), position VARCHAR(50), name VARCHAR(50), mail VARCHAR(50) UNIQUE, hash VARCHAR(50));
#CREATE TABLE positions (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, position_pos VARCHAR(50), reports_pos VARCHAR(50), comp_1 INTEGER, comp_2 INTEGER, comp_3 INTEGER, comp_4 INTEGER, comp_5 INTEGER, comp_6 INTEGER, comp_7 INTEGER, comp_8 INTEGER, comp_9 INTEGER);
#CREATE TABLE test_results (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, mail VARCHAR(50), reliability INTEGER,	discipline INTEGER,	executive INTEGER,	responsibility INTEGER,	resolved INTEGER,	organizational INTEGER,	software INTEGER,	adaptation INTEGER,	planning INTEGER,	page INTEGER,	strengthening INTEGER,	building_on_achievements INTEGER,	building_for_development INTEGER,	innovation INTEGER,	approved INTEGER,	loyalty INTEGER,	currency INTEGER,	country INTEGER,	preparedness_for_compromise INTEGER,	cooperation INTEGER,	openness INTEGER,	openness_of_feedback INTEGER,	clientoority INTEGER,	customer_needs_orientation INTEGER,	partnership INTEGER,	adoption_of_decisions INTEGER,	systemic_thinking INTEGER,	business INTEGER,	forward_thinking INTEGER,	effective_communication INTEGER,	clean_communication INTEGER,	impunity_and_influence INTEGER,	negotiations INTEGER,	cross_functional_interaction INTEGER,	informal_leadership INTEGER,	management INTEGER,	implementation_management INTEGER,	motivation_of_subordinates INTEGER,	organization_of_work INTEGER,	change_management INTEGER,	development_of_subordinates INTEGER, command_management INTEGER);
#INSERT INTO test_results (mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management ) VALUES ('123@ed.er1' , 4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,34,4,4,4,44,4,4,4,4,4,44);
#INSERT INTO test_results (mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management ) VALUES ('123@ed.er2' , 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42);