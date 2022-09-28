

from flask import Flask, redirect, render_template, request, session, flash
from flask_mail import Mail, Message
from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from config import host, user, password, db_name, Config
from helpers import apology, login_required, createPassword, checkPassword, checkPasswordBadSymbol, checkUsername, checkUsernameMastContain, escape 
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import csv
import pandas as pd
import datetime
from forms import ContactForm
from werkzeug.exceptions import HTTPException
import time
from decorator import send_message_head, send_message_manager, upload_test_results, \
                    upload_file_users, allowed_file, download_file_to_user, connection_db, \
                    create_summary_table_to_download, create_positions_table_to_download
import constants

#from flask_sqlalchemy import SQLAlchemy


# Configure application
app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
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
    if session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH:
        status = session["user_status"]
        return render_template('index.html', status = status)
    elif session["user_status"] == constants.HEAD:
        return render_template("/instruction_for_head.html")
    elif session["user_status"] == constants.MANAGER:
        return render_template("/instruction_for_manager.html")
    else:
        return redirect("/login")


@app.route('/log_table')
@login_required
def log_table():
    if session['user_status'] == constants.ADMIN:
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, mail, status, date FROM log_table ORDER BY date DESC")
                log_data = cursor.fetchall()
                cursor.execute("SELECT exception_data, exception_code, user_mail, user_status, exception_date FROM exception_table ORDER BY exception_date DESC")
                exception_table = cursor.fetchall()
                return render_template('log_table.html', log_data = log_data, exception_table = exception_table)
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
    else:
        return redirect('/')


@app.route("/positions", methods=['POST','GET'])
@login_required
def positions():
    readyStatusList = ['Все', 'Заполнено', 'Не заполнено']
    if request.method == 'GET' and (session["user_status"] == constants.ADMIN \
                        or session["user_status"] == constants.COACH):
        try:
            connection = connection_db() 
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM positions WHERE reports_pos in \
                                (SELECT mail FROM users WHERE status = %(status)s) \
                                ORDER BY reports_pos ", {'status': constants.HEAD})
                positions = cursor.fetchall()
                cursor.execute("SELECT DISTINCT reports_pos FROM positions WHERE reports_pos in \
                                (SELECT mail FROM users WHERE status = %(status)s) \
                                ORDER BY reports_pos", {'status': constants.HEAD})
                headList = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return render_template('positions.html', positions = positions, headList = headList,
                                readyStatusList = readyStatusList, competence = constants.COMPETENCE)

    elif request.method == 'POST' and (session["user_status"] == constants.ADMIN \
                            or session["user_status"] == constants.COACH):
        print('[INFO] route: /positions. method: POST')
        reports_to = request.form.get('reports_to')
        ready_status = request.form.get('ready_status')
        search = request.form.get('search')
        position_edit = request.form.get('position_edit')
        reports_to_edit = request.form.get('reports_to_edit')
        edit = request.form.get('edit')
        edit_save = request.form.get('edit_save')
    
        if not reports_to and not ready_status and not search and not edit and not edit_save:
            return redirect ('/positions')
        try:
            connection = connection_db()
            with connection.cursor() as cursor:
                if edit_save:
                    reports_to = request.form.get('reports_to_edit')
                    position_edit = request.form.get('position_edit')
                    comp_1 = request.form.get('comp_1')
                    comp_2 = request.form.get('comp_2')
                    comp_3 = request.form.get('comp_3')
                    comp_4 = request.form.get('comp_4')
                    comp_5 = request.form.get('comp_5')
                    comp_6 = request.form.get('comp_6')
                    comp_7 = request.form.get('comp_7')
                    comp_8 = request.form.get('comp_8')
                    comp_9 = request.form.get('comp_9')
                    print(f'reprts_to - {reports_to}; position_edit - {position_edit}')
                    cursor.execute("UPDATE positions SET comp_1 = %(comp_1)s, \
                                    comp_2 = %(comp_2)s, comp_3 = %(comp_3)s, comp_4 = %(comp_4)s, \
                                    comp_5 = %(comp_5)s, comp_6 = %(comp_6)s, comp_7 = %(comp_7)s, \
                                    comp_8 = %(comp_8)s, comp_9 = %(comp_9)s \
                                    WHERE position_pos = %(position_pos)s and reports_pos = %(mail)s", \
                                    {'comp_1': comp_1, 'comp_2':comp_2, 'comp_3': comp_3, 'comp_4': comp_4, \
                                    'comp_5': comp_5, 'comp_6': comp_6, 'comp_7': comp_7, 'comp_8':comp_8, \
                                    'comp_9': comp_9, 'position_pos': position_edit, 'mail': reports_to })
                    flash("Изменения сохранены.")
                    if edit == 'editFromUsers':
                        cursor.execute("SELECT mail FROM users WHERE position = %(position_edit)s \
                                        AND reports_to = %(reports_to_edit)s", \
                                        {'position_edit': position_edit, 'reports_to_edit': reports_to_edit})
                        user_mail = cursor.fetchall()
                        return render_template('summary_table.html', user_mail = user_mail[0][0])
                    return redirect('/positions')
                if edit:
                    user_name = request.form.get("user_name")
                    cursor.execute("SELECT * FROM positions WHERE position_pos = %(position_edit)s \
                                    AND reports_pos = %(reports_to_edit)s ORDER BY reports_pos", {'position_edit': position_edit, \
                                    'reports_to_edit': reports_to_edit})
                    position_edit = cursor.fetchall()
                    if user_name:
                        return render_template('positions.html', position_edit = position_edit, competence = constants.COMPETENCE, editValue = edit, user_name = user_name)
                    else:
                        return render_template('positions.html', position_edit = position_edit, competence = constants.COMPETENCE, editValue = edit)

                if search:
                    cursor.execute("SELECT * FROM positions WHERE reports_pos LIKE %(reports_pos)s AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'reports_pos': search, 'status': constants.HEAD})
                    positions = cursor.fetchall()
                    return render_template('positions.html', positions = positions, competence = constants.COMPETENCE)
                if reports_to and not ready_status:
                    cursor.execute("SELECT * FROM positions  WHERE reports_pos = %(reports_pos)s AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'reports_pos': reports_to, 'status': constants.HEAD})
                    positions = cursor.fetchall()
                elif ready_status and not reports_to:
                    if ready_status == readyStatusList[0]: # all
                        cursor.execute("SELECT * FROM positions WHERE reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'status': constants.HEAD})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[1]: # done
                        cursor.execute("SELECT * FROM positions WHERE comp_1 IS NOT NULL AND comp_2 IS NOT NULL AND comp_3 IS NOT NULL AND comp_4 IS NOT NULL AND comp_5 IS NOT NULL AND comp_6 IS NOT NULL AND comp_7 IS NOT NULL AND comp_8 IS NOT NULL AND comp_9 IS NOT NULL AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'status': constants.HEAD})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[2]: # done not
                        cursor.execute("SELECT * FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'status': constants.HEAD})
                        positions = cursor.fetchall()
                elif  reports_to and ready_status:
                    if ready_status == readyStatusList[0]: # all
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'reports_pos': reports_to, 'status': constants.HEAD})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[1]: # done
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s and comp_1 IS NOT NULL AND comp_2 IS NOT NULL AND comp_3 IS NOT NULL AND comp_4 IS NOT NULL AND comp_5 IS NOT NULL AND comp_6 IS NOT NULL AND comp_7 IS NOT NULL AND comp_8 IS NOT NULL AND comp_9 IS NOT NULL AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'reports_pos': reports_to, 'status': constants.HEAD})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[2]: # done not
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s AND (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) AND reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos" , {'reports_pos': reports_to, 'status': constants.HEAD})
                        positions = cursor.fetchall()
                    
                cursor.execute("SELECT DISTINCT reports_pos FROM positions WHERE reports_pos in (SELECT mail FROM users WHERE status = %(status)s) ORDER BY reports_pos", {'status': constants.HEAD})
                headList = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return render_template('positions.html', reports_to_query = reports_to, ready_status_query = ready_status, positions = positions, headList = headList, readyStatusList = readyStatusList, competence = constants.COMPETENCE)
    
    else:
        return redirect("/")


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "GET":
        if session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users ORDER BY id;")
                    users = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT department FROM users ORDER BY department;")
                    usereDepartment = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT reports_to FROM users ORDER BY reports_to;")
                    usereReports_to = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT status FROM users ORDER BY status;")
                    usereStatus_to = cursor.fetchall()            
                    cursor.execute("SELECT DISTINCT position FROM users ORDER BY position;")
                    userePosition = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT name FROM users ORDER BY name;")
                    usereName = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT mail FROM users ORDER BY mail;")
                    usereMail = cursor.fetchall()
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")

            return render_template("users.html",headers_list = constants.SORTLIST, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, usereName =usereName, usereMail = usereMail, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST)

        elif session["user_status"] == constants.HEAD:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    # Все должности руководителя
                    cursor.execute("SELECT * FROM positions WHERE  reports_pos = %(mail)s ORDER BY positions" , {'mail': session["user_mail"]})
                    allPositionFromList = cursor.fetchall()
                    # Необработанные должности
                    cursor.execute("SELECT * FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) AND reports_pos = %(mail)s ORDER BY positions LIMIT 1", {'mail': session["user_mail"]})
                    positionFromList = cursor.fetchall()
                    # Если есть необработанные должности, то выводим ему в кабинет. Иначе досвидания
                    if len(positionFromList) != 0:
                        return render_template("questions_for_head.html", allPositionFromList = allPositionFromList, positionFromList = positionFromList, competence = constants.COMPETENCE_DESCRIPTION)
                    else:
                        return render_template('theEnd.html')
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
        
        elif session['user_status'] == constants.MANAGER:
            today = datetime.date.today()
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE users SET accept_rules = %(today)s WHERE mail = %(mail)s", {'mail': session['user_mail'], 'today': today})
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
            return render_template("/instruction_for_manager.html", today=today)

    elif request.method == "POST":
        if session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH:
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

                    department = request.form.get("department")
                    reports_to = request.form.get("reports_to")
                    status = request.form.get("status")
                    position  = request.form.get("position")
                    query = request.form.get("query")
                    filtr_sort  = request.form.get("filtr_sort")
                    accept_rules = request.form.get("accept_rules")
                    
                    if accept_rules:
                        if accept_rules == 'Приняли':
                            cursor.execute("SELECT * FROM users WHERE accept_rules IS NOT NULL ORDER BY id")
                        elif accept_rules == 'Не приняли':
                            cursor.execute("SELECT * FROM users WHERE accept_rules IS NULL AND status = %(status)s ORDER BY id", {'status': constants.MANAGER})
                        users = cursor.fetchall()
                        return render_template("users.html", headers_list = constants.SORTLIST, accept_rules_select = accept_rules, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST)


                    if filtr_sort:
                        if filtr_sort == 'Подразделению':
                            cursor.execute("SELECT * FROM users ORDER BY department")
                            users = cursor.fetchall()
                            filtr_sort = 'Подразделению'

                        elif filtr_sort == 'Руководителю':
                            cursor.execute("SELECT * FROM users ORDER BY reports_to")
                            users = cursor.fetchall()
                            filtr_sort = 'Руководителю'

                        elif filtr_sort == 'Статусу':
                            cursor.execute("SELECT * FROM users ORDER BY status")
                            users = cursor.fetchall()
                            filtr_sort = 'Статусу'

                        elif filtr_sort == 'Должности':
                            cursor.execute("SELECT * FROM users ORDER BY position")
                            users = cursor.fetchall()
                            filtr_sort = 'Должности'

                        elif filtr_sort == 'Имени':
                            cursor.execute("SELECT * FROM users ORDER BY name")
                            users = cursor.fetchall()
                            filtr_sort = 'Имени'

                        elif filtr_sort == 'Почте':
                            cursor.execute("SELECT * FROM users ORDER BY mail")
                            users = cursor.fetchall()
                            filtr_sort = 'Почте'
                            
                        return render_template("users.html", headers_list = constants.SORTLIST, filtr_sort_position = filtr_sort, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST)
                       

                    if query:
                        cursor.execute("SELECT * FROM users WHERE mail = %(mail)s ORDER BY id", {'mail': query})
                        users = cursor.fetchall()
                        return render_template("users.html", users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST)
    
                    if not department and not reports_to and not status and not position:
                        cursor.execute("SELECT * FROM users ORDER BY id;")
                        users = cursor.fetchall()

                    elif not reports_to and not status and not position:
                        cursor.execute("SELECT * FROM users WHERE department = %(department)s ORDER BY id", {'department': department})
                        users = cursor.fetchall()
                        print(f'dep - {department}\nusers- {users}')
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
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")

            return render_template("users.html", headers_list = constants.SORTLIST, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST, filtr_department = department, filtr_reports_to = reports_to, filtr_status = status, filtr_position = position)
        
        elif session["user_status"] == constants.HEAD:
            # Получение введенных данных
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

            # Проверка введенных данных
            if not comp_1 or not comp_2 or not comp_3 or not comp_4 or not comp_5 or not comp_6 or not comp_7 or not comp_8 or not comp_9:
                flash("Пожалуйста, укажите все значения")
                return redirect ("/users")
            if  int(comp_1) > 9 or int(comp_1) < 1 or int(comp_2) > 9 or int(comp_2) < 1 or int(comp_3) > 9 or int(comp_3) < 1 or int(comp_4) > 9 or int(comp_4) < 1 or int(comp_5) > 9 or int(comp_5) < 1 or int(comp_6) > 9 or int(comp_6) < 1 or int(comp_7) > 9 or int(comp_7) < 1 or int(comp_8) > 9 or int(comp_8) < 1 or int(comp_9) > 9 or int(comp_9) < 1:
                flash("Пожалуйста, укажите все значения. Значения должны быть в диапазоне от 1 до 9.")
                return redirect ("/users")
            if int(comp_1) == int(comp_2) or int(comp_1) == int(comp_3) or int(comp_1) == int(comp_4) or int(comp_1)  == int(comp_5) or int(comp_1)  == int(comp_6) or int(comp_1)  == int(comp_7) or int(comp_1)  == int(comp_8) or int(comp_1)  == int(comp_9) or int(comp_2)  == int(comp_3) or int(comp_2) == int(comp_4) or int(comp_2) == int(comp_5) or int(comp_2) == int(comp_6) or int(comp_2)  == int(comp_7) or int(comp_2)  == int(comp_8) or int(comp_2)  == int(comp_9) or int(comp_3) == int(comp_4) or int(comp_3) == int(comp_5) or int(comp_3)  == int(comp_6) or int(comp_3) == int(comp_7) or int(comp_3) == int(comp_8) or int(comp_3) == int(comp_9) or int(comp_4) == int(comp_5) or int(comp_4)  == int(comp_6) or int(comp_4)  == int(comp_7) or int(comp_4)  == int(comp_8) or int(comp_4)  == int(comp_9) or int(comp_5)  == int(comp_6) or int(comp_5)  == int(comp_7) or int(comp_5)  == int(comp_8) or int(comp_5)  == int(comp_9) or int(comp_6) == int(comp_7) or int(comp_6)  == int(comp_8) or int(comp_6)  == int(comp_9) or int(comp_7)  == int(comp_8) or int(comp_7)  == int(comp_9) or int(comp_8)  == int(comp_9):
                flash("Значения должны быть уникальными.")
                return redirect ("/users")

            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    # Вносим полученные данные
                    cursor.execute("UPDATE positions SET comp_1 = %(comp_1)s, comp_2 = %(comp_2)s, comp_3 = %(comp_3)s, comp_4 = %(comp_4)s, comp_5 = %(comp_5)s, comp_6 = %(comp_6)s, comp_7 = %(comp_7)s, comp_8 = %(comp_8)s, comp_9 = %(comp_9)s WHERE position_pos = %(position_pos)s and reports_pos = %(mail)s", {'comp_1': comp_1, 'comp_2':comp_2, 'comp_3': comp_3, 'comp_4': comp_4, 'comp_5': comp_5, 'comp_6': comp_6, 'comp_7': comp_7, 'comp_8':comp_8, 'comp_9': comp_9, 'position_pos': position_pos, 'mail': session["user_mail"]})
                    return redirect('/users')
            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")

    else:
        return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    form = ContactForm()
    msg = ""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":    

        if form.validate_on_submit() is False:
            msg = "Ошибка валидации"
            flash("Вы робот?")
            return render_template('/login.html', form = form, msg = msg )

        # Forget any user_id
        session.clear()
        # Ensure username was submitted
        if not request.form.get("mail"):
            #flash('Вы не указали логин')
            return render_template('/login.html', form = form, msg = msg )
           
        # Ensure password was submitted
        elif not request.form.get("hash") or len(request.form.get("hash")) < 3:
            flash('Вы указали неверный пароль')
            return render_template('/login.html', form = form, msg = msg)
            
        # Query database for username
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                mail = request.form.get('mail').lower().strip()
                cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                rows = cursor.fetchall()
                # Ensure username exists and password is correct
                password_req = request.form.get("hash").strip()
                if len(rows) != 1 or not check_password_hash(rows[0][7], password_req):
                    flash('Вы указали неверный логин или пароль')
                    return render_template('/login.html', form = form, msg = msg )
                    #return apology("invalid username and/or password", 403)

                # Remember which user has logged in
                session["user_id"] = rows[0][0]
                session["user_name"] = rows[0][5]
                session["user_status"] = rows[0][3]
                session["user_mail"] = rows[0][6]
                today = datetime.datetime.today().strftime("%d.%m.%Y %X")
               
                #insert in to log table
                cursor.execute("INSERT INTO log_table (name, mail, status, date) VALUES(%(name)s, %(mail)s, %(status)s, %(date)s)", {'name': session["user_name"], 'mail': session["user_mail"], 'status': session["user_status"], 'date': today})

                # Redirect user to home page
                return redirect('/' )

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", form = form, msg = msg)


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
    if request.method == "POST" and (session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH):
        if request.form.get('flag') == 'render':
            userId = request.form.get("user_id")
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True  
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, department, reports_to, status, position, name, mail FROM users WHERE id = %(userId)s", {'userId': userId})
                    userData = cursor.fetchall()

            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
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
            
            return render_template("edit.html", id = id, department = department, reports_to = reports_to, status = status, position = position, name = name, mail = mail, statusList = constants.STATUS_LIST, positionList = constants.POSITIONS_LIST)
        
        elif request.form.get('flag') == 'save':
            id = request.form.get("id")
            department = request.form.get("department").strip()
            reports_to = request.form.get("reports_to").strip()
            status = request.form.get("status").strip()
            position  = request.form.get("position").strip()
            name = request.form.get("name").strip()
            mail = request.form.get("mail").lower().strip()
            hash = request.form.get("hash").strip()
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
            if  hash: #and (status == constants.ADMIN or status == constants.COACH or status == constants.HEAD):
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
                    # если меняли пароль b  если не меняли
                    if hash:
                        cursor.execute("UPDATE users SET department = %(department)s, reports_to = %(reports_to)s, status = %(status)s, position = %(position)s, name = %(name)s, mail = %(mail)s, hash = %(hash)s  WHERE id = %(id)s", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash, 'id': id})
                    else:
                        cursor.execute("UPDATE users SET department = %(department)s, reports_to = %(reports_to)s, status = %(status)s, position = %(position)s, name = %(name)s, mail = %(mail)s WHERE id = %(id)s", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'id': id})
                    
                    # Если изменили должность и такой нет в базе, добавляем
                    # Проверяем существует ли должность в базе. Если нет, то добавляем
                    # Если указан руководитель
                    if reports_to:
                        # Проверяем существует ли должность в базе. Если нет, то добавляем
                        cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s and reports_pos = %(reports_pos)s", {'position': position, 'reports_pos': reports_to})
                        pos = cursor.fetchall()
                        if len(pos) == 0 and status != constants.ADMIN and status != constants.COACH:
                            cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})


            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
            
            flash('Изменения сохранены.')
            return redirect("/users")

        else:
            return redirect('/')
    else:
        return redirect("/")


@app.route("/delete", methods = ["POST"])
@login_required
def delete():
    if request.method == "POST" and (session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH):
        id = request.form.get("id")

        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %(id)s", {'id': id})

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
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
    if request.method == "POST" and (session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH):
        department = request.form.get("department").strip()
        reports_to = request.form.get("reports_to").strip()
        status = request.form.get("status").strip()
        position  = request.form.get("position").strip()
        name = request.form.get("name").strip().strip()
        mail = request.form.get("mail").lower().strip()
        user_password = request.form.get("password").strip()
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
        #if  status == constants.ADMIN or status == constants.COACH or status == constants.HEAD: # and (not hash or checkPassword(hash)):
        if not user_password:
            hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
        else:                
            hash = generate_password_hash(user_password, "pbkdf2:sha256")      
          
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
                
                # Если указан руководитель
                if reports_to:
                    # Проверяем существует ли должность в базе. Если нет, то добавляем
                    cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s and reports_pos = %(reports_pos)s", {'position': position, 'reports_pos': reports_to})
                    pos = cursor.fetchall()
                    if len(pos) == 0 and status != constants.ADMIN and status != constants.COACH:
                        cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
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
    if request.method == "GET" and (session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH):
        return render_template('upload_file.html', typeDataFlag = 'users')

    elif request.method == "POST" and (session["user_status"] == constants.ADMIN or session["user_status"] == constants.COACH):
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        xlsx = pd.ExcelFile(f'{Config.UPLOAD_FOLDER}/{filename}')
        table = xlsx.parse()
        upload_file_users(table, constants.MANAGER, constants.HEAD)
        os.remove(f'{Config.UPLOAD_FOLDER}/{filename}')
        flash(f"Загрузка идет в фоновом режиме")
        return redirect ('/users')

    else:
        return redirect('/')


@app.route('/test_results', methods=['POST', 'GET'])
@login_required
def test_results():
    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        listSize = 'small'
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT name_test, mail, reliability, organizational, strengthening, approved, country, clientoority, adoption_of_decisions, effective_communication, management FROM test_results ORDER BY mail")
                testResults = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Erroe while working with PostgraseSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally :
            if connection:
                connection.close()
                print("[INFO] PostgraseSQL connection closed")  
        return render_template('/test_results.html', testResults = testResults, headerList = constants.HEADER_LIST_FROM_TEST_SMALL, listSize = listSize)
    

    if request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        listSize = request.form.get('listSize')
        user_mail = request.form.get('search')
        from_summary = request.form.get('fromSummary')
        if listSize == 'all':
            # подключаемся к базе и передаем на страницу все результатьы тестов пользователей
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name_test, mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management FROM test_results ORDER BY mail")
                    #cursor.execute("SELECT  test_results.mail, test_results.reliability ,	test_results.discipline ,	test_results.executive ,	test_results.responsibility ,	test_results.resolved ,	test_results.organizational ,	test_results.software ,	test_results.adaptation ,	test_results.planning ,	test_results.page ,	test_results.strengthening ,	test_results.building_on_achievements ,	test_results.building_for_development ,	test_results.innovation ,	test_results.approved ,	test_results.loyalty ,	test_results.currency ,	test_results.country ,	test_results.preparedness_for_compromise ,	test_results.cooperation ,	test_results.openness ,	test_results.openness_of_feedback ,	test_results.clientoority ,	test_results.customer_needs_orientation ,	test_results.partnership ,	test_results.adoption_of_decisions ,	test_results.systemic_thinking ,	test_results.business ,	test_results.forward_thinking ,	test_results.effective_communication ,	test_results.clean_communication ,	test_results.impunity_and_influence ,	test_results.negotiations ,	test_results.cross_functional_interaction ,	test_results.informal_leadership ,	test_results.management ,	test_results.implementation_management ,	test_results.motivation_of_subordinates ,	test_results.organization_of_work ,	test_results.change_management ,	test_results.development_of_subordinates ,	test_results.command_management , users.name AS user_name FROM test_results JOIN users ON test_results.mail = users.mail")
                    testResults = cursor.fetchall()
            except Exception as _ex:
                print("[INFO] Erroe while working with PostgraseSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally :
                if connection:
                    connection.close()
                    print("[INFO] PostgraseSQL connection closed")   
            return render_template('/test_results.html', testResults = testResults, headerList = constants.HEADER_LIST_FROM_TEST, listSize = listSize)
        
        elif listSize == 'small':
            # подключаемся к базе и передаем на страницу все результатьы тестов пользователей
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name_test, mail, reliability, organizational, strengthening, approved, country, clientoority, adoption_of_decisions, effective_communication, management FROM test_results ORDER BY mail")
                    testResults = cursor.fetchall()
            except Exception as _ex:
                print("[INFO] Erroe while working with PostgraseSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally :
                if connection:
                    connection.close()
                    print("[INFO] PostgraseSQL connection closed")  
            return render_template('/test_results.html', testResults = testResults, headerList = constants.HEADER_LIST_FROM_TEST_SMALL, listSize = listSize)

        elif user_mail:
            # подключаемся к базе и передаем на страницу все результатьы тестов пользователей
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name_test, mail, reliability, organizational, strengthening, approved, country, clientoority, adoption_of_decisions, effective_communication, management FROM test_results WHERE mail = %(mail)s", {'mail': user_mail})
                    testResults = cursor.fetchall()
                    print(testResults)
            except Exception as _ex:
                print("[INFO] Erroe while working with PostgraseSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally :
                if connection:
                    connection.close()
                    print("[INFO] PostgraseSQL connection closed") 

            if from_summary:
                 return render_template('/test_results.html', testResults = testResults, headerList = constants.HEADER_LIST_FROM_TEST_SMALL, from_summary = from_summary)
            else:
                return render_template('/test_results.html', testResults = testResults, headerList = constants.HEADER_LIST_FROM_TEST_SMALL)

    else:
        return redirect('/')


@app.route('/file_test', methods = ["GET", "POST"])
@login_required
def file_test():
    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        return render_template('upload_file.html', typeDataFlag = 'results')

    # Описание есть в загрузке файла с пользователями /file
    elif request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            xlsx = pd.ExcelFile(f'{Config.UPLOAD_FOLDER}/{filename}')
            table = xlsx.parse()
            upload_test_results(table)
            os.remove(f'{Config.UPLOAD_FOLDER}/{filename}')
            flash(f"Загрузка идет в фоновом режиме.")
            return redirect ('/test_results')

    else:
        return redirect ('/')


@app.route('/mail_heads', methods = ['GET', 'POST'])
@login_required
def mail_heads():
    # Статусы для фильтра 
    readyStatusList = ['Все', 'Отправлено', 'Не отправлено']
    # Флаг для выбора пути. Одно письмо, всем или токо тем, кто еще не получал приглашение
    flag  = request.form.get('flag')

    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        # Выбираем все пользователей со статусом constants.HEAD  и все почты для поиска
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s ORDER BY id", {'status':constants.HEAD})
                users = cursor.fetchall()
                cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': constants.HEAD})
                headList = cursor.fetchall()
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")
        
        return render_template('mail.html', users = users, headList = headList, readyStatusList = readyStatusList)

    elif request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        reports_to = request.form.get('reports_to')
        ready_status = request.form.get('ready_status')
        search = request.form.get('search')
        ranking_done = request.form.get('ranking_done')

        # Данные для фитра и поиска
        if reports_to or ready_status or search or ranking_done:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s \
                        ORDER BY mail", {'status': constants.HEAD})
                    headList = cursor.fetchall()

                    if reports_to and not ready_status:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                            FROM users WHERE status = %(status)s \
                            AND mail = %(reports_to)s ORDER BY id", {'status':constants.HEAD, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif ready_status and not reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s \
                                AND mail_date IS NOT NULL ORDER BY id", {'status':constants.HEAD})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s AND mail_date IS NULL \
                                ORDER BY id", {'status':constants.HEAD})
                            users = cursor.fetchall()
                        else:
                            return redirect('/mail_heads')
                    elif ready_status and reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s AND mail_date IS NOT NULL AND mail = %(reports_to)s \
                                ORDER BY id", {'status':constants.HEAD, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s AND mail_date IS NULL AND mail = %(reports_to)s \
                                ORDER BY id", {'status':constants.HEAD, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        else:
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s and mail = %(reports_to)s ORDER BY id", {'status':constants.HEAD, 'reports_to': reports_to})
                            users = cursor.fetchall()
                    elif search:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users \
                            WHERE status = %(status)s and mail = %(search)s ORDER BY id", {'status':constants.HEAD, 'search': search})
                        users = cursor.fetchall()
                    elif ranking_done:
                        if ranking_done == 'Заполнил':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users \
                                WHERE status = %(status)s and mail in \
                                (SELECT reports_pos FROM positions \
                                    WHERE (comp_1 IS NOT NULL AND comp_2 IS NOT NULL AND comp_3 IS NOT NULL \
                                    AND comp_4 IS NOT NULL AND comp_5 IS NOT NULL AND comp_6 IS NOT NULL \
                                    AND comp_7 IS NOT NULL AND comp_8 IS NOT NULL AND comp_9 IS NOT NULL)) \
                                ORDER BY mail_date", {'status': constants.HEAD})
                            users = cursor.fetchall()
                        elif ranking_done == 'Не заполнил':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date \
                                FROM users WHERE status = %(status)s and mail in \
                                (SELECT reports_pos FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL \
                                    OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL \
                                    OR comp_9 IS NULL)) ORDER BY mail_date", {'status':constants.HEAD})
                            users = cursor.fetchall()
        
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/mail_heads')            
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")

            return render_template('mail.html', users = users, headList = headList, readyStatusList = readyStatusList, 
                                   reports_to_query = reports_to, ready_status_query = ready_status, ranking_done_status = ranking_done)        
                
        # if single send mode (Оставляем)
        if flag == 'single':
            user_name = request.form.get('user_name')
            user_mail = request.form.get('user_mail')
            # conect to database
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    try:
                        # create date, password and message
                        today = datetime.date.today()
                        user_password = createPassword()
                        hash = generate_password_hash(user_password, "pbkdf2:sha256")
                        # check mail date
                        cursor.execute("SELECT mail_date FROM users WHERE mail = %(mail)s", {'mail':user_mail})
                        mail_date = cursor.fetchall()
                        msg = Message('Проект «Развитие компетенций сотрудников back-office»', recipients=[user_mail])
                        # If the invitation was sent
                        if mail_date[0][0] != None:
                            cursor.execute("SELECT reports_pos FROM positions WHERE reports_pos = %(mail)s AND (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL)", {'mail':user_mail})
                            comp = cursor.fetchall()
                            if len(comp) != 0:
                                msg.body = render_template("reminder_to_head.txt", user_name = user_name, user_mail = user_mail, user_password = user_password)
                                msg.html = render_template("reminder_to_head.html", user_name = user_name, user_mail = user_mail, user_password = user_password)
                            else:
                                flash("Сообщение не отправлено, т.к. данный руководитель заполнил все данные.")
                                return redirect('/mail_heads')
                        else:
                            msg.body = render_template("to_head_email.txt", user_name = user_name, user_mail = user_mail, user_password = user_password)
                            msg.html = render_template("to_head_email.html", user_name = user_name, user_mail = user_mail, user_password = user_password)
                        
                        mail.send(msg)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})

                    except Exception as _ex:
                        flash("Сообщение не отправлено. Проверьте коректно ли указана электронная почта.")
                        print(f'[INFO] Error while working mail sender', _ex)
                        return redirect('/mail_heads')

                    
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
                    
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")
            flash(f'Приглашение отправлено')
            return redirect('/mail_heads')

        # if all send mode (Оставлять)
        elif flag == 'all_invite': 
            send_message_head(constants.HEAD)
            flash(f'Процесс отправки сообщений идет в фоновом режиме')
            return redirect('/mail_heads')


    elif request.method == 'POST' and session['user_status'] == constants.HEAD:
        # сообщение от пользователя в конце опросника
        if flag == 'mail_from_head_end':
            message_from_head = request.form.get('messege_from_head')
            if message_from_head:  
                try:
                    head_mail = session['user_mail']
                    head_name = session['user_name']
                    msg = Message("From Burusan's project", recipients=[constants.HEAD_COACH_EMAIL])
                    msg.body = render_template("from_head_email.txt", head_name = head_name, head_mail = head_mail, message_from_head = message_from_head)
                    msg.html = render_template('from_head_email.html', head_name = head_name, head_mail = head_mail, message_from_head = message_from_head)
                    mail.send(msg)
                    print(f'[INFO] Message has bin sent via mail sender.')
                    flash(f"Сообщение отправлено. Спасибо!")
                    return render_template('theEnd.html')
                except Exception as _ex:
                    print(f'[INFO] Error while working mail sender:', _ex)
                    flash(f"В процессе отправки сообщения произошла ошибка.\nПожалуйста, обновите страницу и повторите попытку.")
                    return render_template('theEnd.html')
            else:
                flash(f"Вы попытались отправить пустое сообщение.\nПожалуйста, введите текст сообщение и повторите попытку.")
                return render_template('theEnd.html')

        # сообщение от пользователя в начале опросника
        elif flag == 'mail_from_head_start':
            message_from_head = request.form.get('messege_from_head')
            if message_from_head:  
                try:
                    head_mail = session['user_mail']
                    head_name = session['user_name']
                    msg = Message("From Burusan's project", recipients=[constants.HEAD_COACH_EMAIL])
                    msg.body = render_template("from_head_email.txt", head_name = head_name, head_mail = head_mail, message_from_head = message_from_head)
                    msg.html = render_template('from_head_email.html', head_name = head_name, head_mail = head_mail, message_from_head = message_from_head)
                    mail.send(msg)
                    print(f'[INFO] Message has bin sent via mail sender.')
                    flash(f"Сообщение отправлено. Спасибо!")
                    return redirect('/')
                except Exception as _ex:
                    print(f'[INFO] Error while working mail sender:', _ex)
                    flash(f"В процессе отправки сообщения произошла ошибка.\nПожалуйста, обновите страницу и повторите попытку.")
                    return redirect('/')
            else:
                flash(f"Вы попытались отправить пустое сообщение. Пожалуйста, введите текст сообщение и повторите попытку.")
                return redirect('/')

    else:
        return redirect('/')


@app.route('/reset_password', methods = ['GET', 'POST'])
def reset_password():
    form = ContactForm()
    msg_cap = ""
    if request.method == 'GET':
        return render_template('/reset_password.html', form = form, msg = msg_cap)

    elif request.method == 'POST':
        if form.validate_on_submit() is False:
            msg_cap = "Ошибка валидации"
            flash("Вы робот?")
            return render_template('/reset_password.html', form = form, msg = msg_cap )

        user_name = request.form.get('username')
        if user_name:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    # Проверка на существование пользователя
                    cursor.execute("SELECT mail, name, status FROM users WHERE mail = %(mail)s", {'mail': user_name})
                    us = cursor.fetchall()
                    #status = us[0][2]
                    if len(us) == 1: #and (status == constants.COACH or status == constants.ADMIN or status == constants.HEAD):
                        user_password = createPassword()
                        hash = generate_password_hash(user_password, "pbkdf2:sha256")
                        user_name = us[0][0]
                        name = us[0][1]
                        try:
                            msg = Message('From STI-Partners', recipients=[user_name])
                            msg.body = render_template("mail_reset_password.txt", user_name = name, user_password = user_password)
                            msg.html = render_template("mail_reset_password.html", user_name = name, user_password = user_password)
                            mail.send(msg)

                        except Exception as _ex:
                            print('[INFO] Error while working mail sender', _ex)
                            flash("В процессе создания запроса произошла ошибка. Пожалуйста, обновите страницу и повторите попытку.")
                            return render_template('/reset_password.html', form = form, msg = msg_cap )

                        cursor.execute("UPDATE users SET hash = %(hash)s WHERE mail = %(mail)s", {'hash': hash, 'mail': user_name})
                        flash('Проверьте свою электронную почту. Если ваш email зарегистрирован в систему, то вы получите письмо с данными для входа.')
                        return render_template('/login.html', form = form, msg = msg_cap)

                    else:
                        flash('Проверьте свою электронную почту. Если ваш email зарегистрирован в систему, то вы получите письмо с данными для входа.')
                        return render_template('/login.html', form = form, msg = msg_cap)

            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash("В процессе создания запроса произошла ошибка. Пожалуйста, обновите страницу и повторите попытку.")
                return render_template('reset_password.html', form = form, msg = msg_cap)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
        else:
            flash('Укажите адрес электронной почты и повторите запрос')
            return redirect('reset_password', form = form, msg = msg_cap)

    else:
        return redirect('/')


@app.route('/summary', methods = ['GET', 'POST'])
@login_required
def summary():
    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        allManagers = create_summary_table_to_download()

        # Передаем данные для создания страницы        
        return render_template('/summary_table_all_managers.html',  allManagers = allManagers)

    elif request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        # почта запрашиваемого пользователя
        userMail = request.form.get('userMail')
        # Если запрос пришел из общей сводной таблицы
        fromAllTAble = request.form.get('fromAllTable')

        # Подключение к базе данных
        try:
            connection = connection_db()
            with connection.cursor() as cursor:
                # Данные пользователя
                cursor.execute("SELECT id, name, mail, department, position, reports_to, mail_date, accept_rules FROM users WHERE mail = %(mail)s ", {'mail': userMail})
                userData = cursor.fetchall()

                # Важнейшие компетенции
                cursor.execute("SELECT comp_1, comp_2, comp_3, comp_4, comp_5,comp_6, comp_7, comp_8, comp_9 FROM positions WHERE reports_pos = %(reports_to)s AND position_pos = %(position)s", {'reports_to': userData[0][5], 'position': userData[0][4]})
                topCompetence = cursor.fetchall()
                
                 # Результаты тестирования
                cursor.execute("SELECT reliability, organizational, strengthening, approved, country, clientoority, adoption_of_decisions, effective_communication, management FROM test_results WHERE mail = %(userMail)s", {'userMail': userMail})
                testResults = cursor.fetchall() 
                
                # Если нет результатов тестирования
                if len(testResults) == 0:
                    testResults.append((0,0,0,0,0,0,0,0,0))
                
                # общий словарь
                summaryDict = {}
                for i in range(9):
                    summaryDict[f'comp_{i+1}'] = (constants.HEADER_LIST_FROM_TEST_SMALL[i], topCompetence[0][i], testResults[0][i])
                
                # Словарь для сортировки по важности
                topCompetenceDict = {}
                i = 1
                for comp in topCompetence[0]:
                    topCompetenceDict[f'comp_{i}'] = comp
                    i = i + 1

                # Сортировка по важности и запись ключа в новый список
                newCompRang = []

                # Если есть неранжированные компетенции, то ранжируем их цифрой 10
                for comp in topCompetenceDict:
                    if topCompetenceDict[comp] == None:
                        topCompetenceDict[comp] = 0

                # Добавляем в список компетенции по возростанию 
                for comp in topCompetenceDict:
                    x = min(topCompetenceDict, key=topCompetenceDict.get)
                    newCompRang.append(x)
                    topCompetenceDict[x] = 10


                # Create table whith course and insert into data
                print(f'summaryDict {summaryDict};\nnewCompRang - {newCompRang}')

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        # Создаем страницу       
        return render_template('/summary_table.html',  userData = userData, summaryDict = summaryDict, newCompRang = newCompRang, fromAllTAble = fromAllTAble)

    else:
        return redirect('/')


@app.route('/mail_manager', methods = ['GET', 'POST'])
@login_required
def mail_manager():
    # создаем списки и счетчики отправленных и неотправленных сообщений
    notSendList = []
    counterSend = 0
    counterNotSend = 0
    # Статусы для фильтра 
    readyStatusList = ['Все', 'Отправлено', 'Не отправлено']
    # Флаг для выбора пути. Одно письмо, всем или токо тем, кто еще не получал приглашение
    flag  = request.form.get('flag')

    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        # Выбираем все пользователей со статусоv MANAGER  и все почты для поиска
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                    FROM users WHERE status = %(status)s ORDER BY id", {'status': constants.MANAGER})
                users = cursor.fetchall()
                cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': constants.MANAGER})
                headList = cursor.fetchall()
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")
        
        return render_template('mail_manager.html', users = users, headList = headList, readyStatusList = readyStatusList)

    elif request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        reports_to = request.form.get('reports_to')
        ready_status = request.form.get('ready_status')
        search = request.form.get('search')
        rules = request.form.get('rules')

        # Данные для фитра и поиска
        if reports_to or ready_status or search or rules:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': constants.MANAGER})
                    headList = cursor.fetchall()

                    if reports_to and not ready_status:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules  \
                            FROM users WHERE status = %(status)s  and mail = %(reports_to)s ORDER BY id", {'status':constants.MANAGER, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif ready_status and not reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND mail_date IS NOT NULL ORDER BY id", {'status':constants.MANAGER})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND mail_date IS NULL ORDER BY id", {'status':constants.MANAGER})
                            users = cursor.fetchall()
                        else:
                            return redirect('/mail_manager')
                    elif ready_status and reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND mail_date IS NOT NULL AND mail = %(reports_to)s \
                                ORDER BY id", {'status':constants.MANAGER, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND mail_date IS NULL AND mail = %(reports_to)s \
                                ORDER BY id", {'status':constants.MANAGER, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        else:
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s and mail = %(reports_to)s \
                                ORDER BY id", {'status':constants.MANAGER, 'reports_to': reports_to})
                            users = cursor.fetchall()
                    elif search:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                            FROM users WHERE status = %(status)s and mail = %(search)s \
                            ORDER BY id", {'status':constants.MANAGER, 'search': search})
                        users = cursor.fetchall()
                    elif rules:
                        if rules == 'Принял':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND accept_rules IS NOT NULL ORDER BY mail_date", {'status':constants.MANAGER})
                            users = cursor.fetchall()
                        elif rules == 'Не принял':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s AND accept_rules IS NULL  ORDER BY mail_date", {'status':constants.MANAGER})
                            users = cursor.fetchall()

        
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/mail_manager')            
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")

            return render_template('mail_manager.html', users = users, headList = headList, readyStatusList = readyStatusList, 
                                    reports_to_query = reports_to, ready_status_query = ready_status, rules_status = rules)        
               
         # if single send mode
        if flag == 'single':
            user_name = request.form.get('user_name')
            user_mail = request.form.get('user_mail')
            
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    try:
                        # create date, password and message
                        today = datetime.date.today()
                        user_password = createPassword()
                        hash = generate_password_hash(user_password, "pbkdf2:sha256")
                        msg = Message('Проект «Развитие компетенций сотрудников back-office»', recipients=[user_mail])

                        cursor.execute("SELECT mail_date FROM users WHERE mail = %(mail)s", {'mail': user_mail})
                        mail_date = cursor.fetchall()
                        if mail_date[0][0] != None:

                            cursor.execute("SELECT accept_rules FROM users WHERE mail = %(mail)s", {'mail': user_mail})
                            accept_rules = cursor.fetchall()
                            if accept_rules[0][0] == None:
                                msg.body = render_template("reminder_to_manager.txt", user_name = user_name, 
                                                            user_mail = user_mail, user_password = user_password)
                                msg.html = render_template("reminder_to_manager.html", user_name = user_name, 
                                                            user_mail = user_mail, user_password = user_password)
                            else:
                                flash("Сообщение не отправлено, т.к. данный сотрудник принял условия.")
                                return redirect('/mail_manager')
                        else:
                            msg.body = render_template("to_manager_email.txt", user_name = user_name, 
                                                        user_mail = user_mail, user_password = user_password)
                            msg.html = render_template("to_manager_email.html", user_name = user_name, 
                                                        user_mail = user_mail, user_password = user_password)

                        mail.send(msg)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                            WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})

                    except Exception as _ex:
                        flash("Сообщение не отправлено. Проверьте коректно ли указана электронная почта.")
                        print(f'[INFO] Error while working mail sender', _ex)
                        return redirect('/mail_manager')
                                        
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
                    
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")
            
            flash(f'Приглашение отправлено')
            return redirect('/mail_manager')    

        elif flag == 'all_invite':
            send_message_manager(constants.MANAGER)
            flash(f'Процесс отправки сообщений идет в фоновом режиме')
            return redirect('/mail_manager')

        elif flag == 'has_not_invite':
            print(flag)
            today = datetime.date.today()
            try: 
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    # default value mail_date is -
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail_date IS NULL", {'status':constants.MANAGER})
                    users = cursor.fetchall()
                    for singleUser in users:
                        try:
                            user_password = createPassword()
                            hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                            msg = Message("From STI-Partners", recipients=[singleUser[5]])
                            msg.body = render_template("to_manager_email.txt", user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            msg.html = render_template('to_manager_email.html', user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            mail.send(msg)
                            counterSend = counterSend + 1
                            cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':singleUser[5]})
                            print(f'[INFO] Message has bin sent via mail sender.')
                        except Exception as _ex:
                            notSendList.append(singleUser)
                            counterNotSend = counterNotSend + 1 
                            print(f'[INFO] Error while working mail sender:', _ex)

                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':constants.MANAGER})
                    users = cursor.fetchall()

            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL:', _ex)
                x = 1
                notSendList.append(singleUser)
                counterNotSend = counterNotSend + 1 
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print(f"[INFO] PostgresSQL nonnection closed")

            flash(f'Приглашение отправлено {counterSend}. Не удалось отправить {counterNotSend} сообщений.')
            return render_template('mail_manager.html', users = users, notSendList = notSendList)

    elif request.method == 'POST' and session['user_status'] == constants.MANAGER:
        # сообщение от пользователя в конце опросника
        # сообщение от пользователя в начале опросника
        if flag == 'mail_from_manager_start':
            message_from_manager = request.form.get('messege_from_manager')
            if message_from_manager:  
                try:
                    head_mail = session['user_mail']
                    head_name = session['user_name']
                    msg = Message("From Burusan's project", recipients=[constants.HEAD_COACH_EMAIL])
                    msg.body = render_template("from_manager_email.txt", head_name = head_name, head_mail = head_mail, message_from_head = message_from_manager)
                    msg.html = render_template('from_manager_email.html', head_name = head_name, head_mail = head_mail, message_from_head = message_from_manager)
                    mail.send(msg)
                    print(f'[INFO] Message has bin sent via mail sender.')
                    flash(f"Сообщение отправлено. Спасибо!")
                    return redirect('/')
                except Exception as _ex:
                    print(f'[INFO] Error while working mail sender:', _ex)
                    flash(f"В процессе отправки сообщения произошла ошибка.\nПожалуйста, обновите страницу и повторите попытку.")
                    return redirect('/')
            else:
                flash(f"Вы попытались отправить пустое сообщение. Пожалуйста, введите текст сообщение и повторите попытку.")
                return redirect('/')
                
    else:
        return redirect('/')


@app.route('/not_done', methods = ['GET', 'POST'])
@login_required
def not_done():
    if request.method == "GET" and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        try:
            connection = connection_db()
            with connection.cursor() as cursos:
               
                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE mail IN (SELECT mail FROM log_table) \
                                AND mail IN \
                                    (SELECT reports_pos FROM positions WHERE \
                                    comp_1 IS NOT NULL OR comp_2 IS NOT NULL OR comp_3 IS NOT NULL\
                                    OR comp_4 IS NOT NULL OR comp_5 IS NOT NULL OR comp_6 IS NOT NULL \
                                    OR comp_7 IS NOT NULL OR comp_8 IS NOT NULL OR comp_9 IS NOT NULL) \
                                ")
                heads_come_and_done = cursos.fetchall()

                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE mail IN (SELECT mail FROM log_table) \
                                AND mail IN \
                                    (SELECT reports_pos FROM positions WHERE \
                                    comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL\
                                    OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL \
                                    OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) \
                                ")
                heads_come_not_done = cursos.fetchall()

                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE mail NOT IN (SELECT mail FROM log_table) \
                                AND status = %(status)s", {'status': constants.HEAD})
                heads_not_come = cursos.fetchall()



                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE mail in (SELECT mail DISTINCT FROM log_table) \
                                AND accept_rules IS NULL AND status = %(status)s", {'status': constants.MANAGER}) 
                managers_come_not_done = cursos.fetchall()

                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE mail NOT IN (SELECT mail DISTINCT FROM log_table) \
                                AND status = %(status)s", {'status': constants.MANAGER}) 
                managers_not_come = cursos.fetchall()

                cursos.execute("SELECT name, mail, status, reports_to FROM users \
                                WHERE accept_rules IS NOT NULL AND status = %(status)s", {'status': constants.MANAGER}) 
                managers_come_and_done = cursos.fetchall()

        except Exception as _ex:
            print(f'[INFO] {_ex}')
            return redirect('/')
        finally:
            if connection:
                connection.close()

    elif request.method == "POST":
        pass
    return render_template('/not_done.html', \
                heads_come_and_done = heads_come_and_done,\
                heads_come_not_done = heads_come_not_done, \
                heads_not_come = heads_not_come,\
                managers_come_not_done = managers_come_not_done,\
                managers_not_come = managers_not_come,\
                managers_come_and_done = managers_come_and_done\
                )
    

@app.errorhandler(Exception)
def handle_exception(e):    
    today = datetime.datetime.today().strftime("%d.%m.%Y %X")
    user_mail = session['user_mail']
    user_status = session['user_status']
    if isinstance(e, HTTPException):
        code = e.code
        name = e.name
        print(f'[INFO] HTTPException: {code} {name}')
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO exception_table (exception_code, exception_data, exception_date, user_mail, user_status) VALUES(%(code)s, %(name)s, %(today)s, %(user_mail)s, %(user_status)s)", {'name': name, 'code': code, 'today': today, 'user_mail': user_mail, 'user_status': user_status})
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        return render_template("apology.html", top=code, bottom = escape(name), name = name), 400
    else:
        print(f'[INFO] Exception: {e}')
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO exception_table (exception_code, exception_data, exception_date, user_mail, user_status) VALUES('500', %(name)s,  %(today)s, %(user_mail)s, %(user_status)s)", {'name': e, 'today': today, 'user_mail':user_mail, 'user_status': user_status})
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        return render_template("apology.html", top='500', bottom = e), 500
                
    
@app.route('/settings', methods = ["GET", "POST"])
@login_required
def settings():
    if request.method == 'GET' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        return render_template('/settings.html')
    if request.method == 'POST' and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        invite_head = request.form.get('invite_head')
        reminder_head = request.form.get('reminder_head') 
        invite_manager = request.form.get('invite_manager') 
        reminder_manager = request.form.get('reminder_manager')
        res_password = request.form.get('res_password')

        if invite_head:
            return render_template('to_head_email.html', user_name = 'Иван Иванович', user_mail = 'ivan@example.com', user_password = 'xxxxxxxx')
        if reminder_head:
            return render_template('reminder_to_head.html', user_name = 'Иван Иванович', user_mail = 'ivan@example.com', user_password = 'xxxxxxxx')
        if invite_manager:
            return render_template('to_manager_email.html', user_name = 'Иван Иванович', user_mail = 'ivan@example.com', user_password = 'xxxxxxxx')
        if reminder_manager:
            return render_template('reminder_to_manager.html', user_name = 'Иван Иванович', user_mail = 'ivan@example.com', user_password = 'xxxxxxxx')
        if res_password:
            return render_template('mail_reset_password.html', user_name = 'Иван Иванович', user_mail = 'ivan@example.com', user_password = 'xxxxxxxx')
        else:
            return redirect ('/settings')
    else:
        return redirect ('/')
    

@app.route('/download', methods=["GET", "POST"])
@login_required
def download():
    if request.method == "GET" and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        return render_template("download.html")

    elif request.method == "POST" and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        today = datetime.datetime.now()
        if request.form.get('download_file') == 'positions':
            data_to_download = create_positions_table_to_download()
            file_name = 'Ранжирование компетенций по должностям.xlsx'
            col0, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = '', "Должность",\
                    "Руководитель", constants.COMPETENCE[0], constants.COMPETENCE[1], \
                    constants.COMPETENCE[2], constants.COMPETENCE[3], \
                    constants.COMPETENCE[4], constants.COMPETENCE[5], \
                    constants.COMPETENCE[6], constants.COMPETENCE[7],\
                    constants.COMPETENCE[8]
                    
            number, positionsList,  reportsLiast, comp1, comp2, comp3,\
                    comp4, comp5, comp6, comp7, comp8, comp9 = \
                    [], [], [], [], [], [], [], [], [], [], [], []
            for i, user in enumerate(data_to_download, start=1):
                number.append(i)
                positionsList.append(user[1])
                reportsLiast.append(user[2])
                comp1.append(user[3])
                comp2.append(user[4])
                comp3.append(user[5])
                comp4.append(user[6])
                comp5.append(user[7])
                comp6.append(user[8])
                comp7.append(user[9])
                comp8.append(user[10])
                comp9.append(user[11])

            df = pd.DataFrame({col0: number, col1: positionsList, col2: reportsLiast, \
                col3: comp1, col4: comp2, col5: comp3, col6: comp4, \
                col7: comp5, col8: comp6, col9: comp7, col10: comp8, col11: comp9})

        elif request.form.get('download_file') == 'summary':
            data_to_download = create_summary_table_to_download()
            file_name = 'Итоговая таблица.xlsx'
            col0, col1, col2, col3, col4, col5, col6, col7, col8 = '', "eMail",\
                 "Имя", 'Фамилия', 'Приоритет 1', 'Приоритет 2', 'Приоритет 3',\
                 'Приоритет 4', 'Приоритет 5'
            number, nameList, lastName, eMailList, priority1, priority2, priority3,\
                    priority4, priority5 = [], [], [], [], [], [], [], [], []
        
            for i, user in enumerate(data_to_download, start=1):
                number.append(i)
                name = user[0].split()
                nameList.append(name[0])
                if len(name) == 3:
                    lastName.append(f'{name[1]}{name[2]}')
                else:
                    lastName.append(name[1])
                eMailList.append(user[1])
                priority1.append(user[2])
                priority2.append(user[3])
                priority3.append(user[4])
                priority4.append(user[5])
                priority5.append(user[6])

            
            df = pd.DataFrame({col0: number, col1: eMailList, col2: nameList, \
                col3: lastName, col4: priority1, col5: priority2, col6: priority3, \
                col7: priority4, col8: priority5})
        writer = pd.ExcelWriter(file_name)
        df.to_excel(writer, sheet_name='sheet_1', index=False)
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets['sheet_1'].set_column(col_idx, col_idx, column_width)
        writer.save()
        
        x = download_file_to_user(file_name)
        os.remove(file_name)
        time =  datetime.datetime.now() - today
        print(f'Time - {time}')
        return x
    else:
        return redirect ('/')


@app.route('/hend_accept_rules', methods = ['GET', 'POST'])
@login_required
def hend_accept_rules():
    if request.method == 'GET':
        return render_template('/users')
    elif request.method == "POST" and (session['user_status'] == constants.ADMIN or session['user_status'] == constants.COACH):
        today = datetime.date.today()
        managerMail = request.form.get('mail')
        connection = connection_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET accept_rules = %(today)s WHERE mail = %(mail)s", {'mail': managerMail, 'today': today})
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")
        return redirect('/users')



if __name__ == "__main__":
    app.run()



#CREATE TABLE users (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY NOT NULL, department VARCHAR(150), reports_to VARCHAR(150), status VARCHAR(150), position VARCHAR(150), name VARCHAR(150), mail VARCHAR(150) UNIQUE, hash VARCHAR(300), mail_date VARCHAR(50), division VARCHAR(150), branch VARCHAR(150), accept_rules VARCHAR(50));
#CREATE TABLE positions (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, position_pos VARCHAR(50), reports_pos VARCHAR(50), comp_1 INTEGER, comp_2 INTEGER, comp_3 INTEGER, comp_4 INTEGER, comp_5 INTEGER, comp_6 INTEGER, comp_7 INTEGER, comp_8 INTEGER, comp_9 INTEGER);
#CREATE TABLE test_results (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, name_test VARCHAR(50), mail VARCHAR(50), reliability INTEGER,	discipline INTEGER,	executive INTEGER,	responsibility INTEGER,	resolved INTEGER,	organizational INTEGER,	software INTEGER,	adaptation INTEGER,	planning INTEGER,	page INTEGER,	strengthening INTEGER,	building_on_achievements INTEGER,	building_for_development INTEGER,	innovation INTEGER,	approved INTEGER,	loyalty INTEGER,	currency INTEGER,	country INTEGER,	preparedness_for_compromise INTEGER,	cooperation INTEGER,	openness INTEGER,	openness_of_feedback INTEGER,	clientoority INTEGER,	customer_needs_orientation INTEGER,	partnership INTEGER,	adoption_of_decisions INTEGER,	systemic_thinking INTEGER,	business INTEGER,	forward_thinking INTEGER,	effective_communication INTEGER,	clean_communication INTEGER,	impunity_and_influence INTEGER,	negotiations INTEGER,	cross_functional_interaction INTEGER,	informal_leadership INTEGER,	management INTEGER,	implementation_management INTEGER,	motivation_of_subordinates INTEGER,	organization_of_work INTEGER,	change_management INTEGER,	development_of_subordinates INTEGER, command_management INTEGER);
#CREATE TABLE log_table (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, name VARCHAR(50), mail VARCHAR(50),status VARCHAR(50), date VARCHAR(50) );
#CREATE TABLE Exception (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, except VARCHAR(1000))