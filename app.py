

from crypt import methods
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
from forms import ContactForm
#from flask_sqlalchemy import SQLAlchemy


# Configure application
app = Flask(__name__)

app.config['SECRET_KEY'] = "12345"

app.config['RECAPTCHA_PUBLIC_KEY'] = "6LdoXckhAAAAAIGpoFflYCx7x36jGdtWxn_tSsSd"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LdoXckhAAAAAAXQzdITUL7fts2g6GdHAyVKawaE"

app.config['DEBAG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'backoffice@sti-partners.ru'
app.config['MAIL_PASSWORD'] = 'jz4V4$?9RpiGzVG'
app.config['MAIL_DEFAULT_SENDER'] = 'backoffice@sti-partners.ru'
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

POSITIONS_LIST = ("Директор", "Юрист", "Повар", "Садовник", 'Слесарь', 'DEV', 'Тренер')
STATUS_LIST = ('admin', 'coach', 'manager', 'head')
UPLOAD_FOLDER = 'upload_files'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ADMIN = 'admin'
COACH = 'coach'
HEAD = 'head'
MANAGER = 'manager'
SORTLIST = ("Подразделению", "Руководителю", "Статусу", "Должности", 'Имени', 'Почте')
COMPETENCE = ('Надежность', 'Организованноcть', 'Стремление к совершенству',  'Приверженность', 'Командность', 'Ориентация на клиента', 'Принятие решений', 'Эффективная коммуникация',  'Управленческое мастерство')
COMPETENCE_DESCRIPTION  = (('Надежность', 'Берется за дополнительные задачи и интенсивно работает. Выполняет работу своевременно и несёт ответственность за результаты.'), ('Организованноcть', 'Стремление ставить перед собой четкие цели и планировать работу. Умение быстро адаптироваться к изменениям на работе.'), ('Стремление к совершенству', 'Ставит перед собой амбициозные цели. Обучается новому и совершенствует рабочие процессы.'), ('Приверженность', 'Следует целям и ценностям компании в своей работе. Делится своим опытом с коллегами и партнерами. Шкалы оценки: Лояльность; Взаимовыручка',), ('Командность', 'Объединяет людей и открыто обсуждает рабочие проблемы. Шкалы оценки: Готовность к компромиссу; Сотрудничество; Открытость; Открытость обратной связи'), ('Ориентация на клиента', 'Выясняет потребности клиентов, в том числе внутренних (коллег) и учитывает их в своей работе. Выстраивает долгосрочные отношения. Шкалы оценки: Ориентация на потребности клиента (в том числе внутреннего); Партнерство'), ('Принятие решений', 'Интересуется тенденциями рынка и конкурентами в своей отрасли. Ставит стратегические цели и управляет рисками на основе анализа информации.'), ('Эффективная коммуникация', 'Налаживает контакт с другими людьми и находит индивидуальный подход к собеседнику. Четко и уверенно отстаивает свою позицию.'), ('Управленческое мастерство', 'Организовывает работу подчиненных (коллег) и поддерживает позитивный командный настрой. Развивает и поддерживает подчиненных (коллег).'))
HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ', 'Дисциплинированность', 'Исполнительность', 'Ответственность', 'Решительность', 'ОРГАНИЗОВАННОСТЬ', 'Чёткое целеполагание', 'Адаптивность', 'Планирование', 'Стремление к порядку', 'СТРЕМЛЕНИЕ К СОВЕРШЕНСТВУ', 'Стремление к достижениям', 'Стремление к развитию', 'Инновационность', 'ПРИВЕРЖЕННОСТЬ', 'Лояльность', 'Взаимовыручка', 'КОМАНДНОСТЬ', 'Готовность к компромиссу', 'Сотрудничество', 'Открытость', 'Открытость обратной связи', 'КЛИЕНТООРИЕНТИРОВАННОСТЬ', 'Ориентация на потребности клиента', 'Партнёрство', 'ПРИНЯТИЕ РЕШЕНИЙ', 'Системное мышление', 'Бизнес-мышление', 'Перспективное мышление', 'ЭФФЕКТИВНАЯ КОММУНИКАЦИЯ', 'Чёткая коммуникация', 'Убеждение и влияние', 'Ведение переговоров', 'Кроссфункциональное взаимодействие', 'Неформальное лидерство', 'УПРАВЛЕНЧЕСКОЕ МАСТЕРСТВО', 'Управление исполнением', 'Мотивация подчинённых', 'Организация работы', 'Управление изменениями', 'Развитие подчинённых', 'Управление командой')
HEADER_LIST_FROM_TEST_SMALL = ('НАДЁЖНОСТЬ', 'ОРГАНИЗОВАННОСТЬ', 'СТРЕМЛЕНИЕ К СОВЕРШЕНСТВУ', 'ПРИВЕРЖЕННОСТЬ', 'КОМАНДНОСТЬ', 'КЛИЕНТООРИЕНТИРОВАННОСТЬ', 'ПРИНЯТИЕ РЕШЕНИЙ', 'ЭФФЕКТИВНАЯ КОММУНИКАЦИЯ', 'УПРАВЛЕНЧЕСКОЕ МАСТЕРСТВО')
#HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ', 'Дисциплинированность', 'Исполнительность', 'Ответственность')
#HEADER_LIST_FROM_TEST = ('НАДЁЖНОСТЬ 1', 'Дисциплинированность 2', 'Исполнительность 3', 'Ответственность 4', 'Решительность5', 'ОРГАНИЗОВАННОСТЬ6', 'Чёткое целеполагание7', 'Адаптивность8', 'Планирование9', 'Стремление к порядку10', 'СТРЕМЛЕНИЕ К СОВЕРШЕНСТВУ11', 'Стремление к достижениям12', 'Стремление к развитию13', 'Инновационность14', 'ПРИВЕРЖЕННОСТЬ15', 'Лояльность16', 'Взаимовыручка17', 'КОМАНДНОСТЬ18', 'Готовность к компромиссу19', 'Сотрудничество20', 'Открытость21', 'Открытость обратной связи22', 'КЛИЕНТООРИЕНТИРОВАННОСТЬ23', 'Ориентация на потребности клиента24', 'Партнёрство25', 'ПРИНЯТИЕ РЕШЕНИЙ26', 'Системное мышление27', 'Бизнес-мышление28', 'Перспективное мышление29', 'ЭФФЕКТИВНАЯ КОММУНИКАЦИЯ30', 'Чёткая коммуникация31', 'Убеждение и влияние32', 'Ведение переговоров33', 'Кроссфункциональное взаимодействие34', 'Неформальное лидерство35', 'УПРАВЛЕНЧЕСКОЕ МАСТЕРСТВО36', 'Управление исполнением37', 'Мотивация подчинённых38', 'Организация работы39', 'Управление изменениями40', 'Развитие подчинённых41', 'Управление командой42')
HEAD_COACH_EMAIL = 't.astralenko@sti-partners.ru'
#HEAD_COACH_EMAIL = 'hd.spk27@gmail.com'


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

@app.route('/captcha', methods=["GET", "POST"])
def captcha():
    form = ContactForm()
    msg = ""
    if request.method =='POST':
        if form.validate_on_submit():
            msg = 'Успех'
            # Записать в БД
        else:
            msg = "Ошибка валидации"
            # Обработать ошибку
    return render_template('captcha.html', form = form, msg = msg)


@app.route('/')
@login_required
def index():
    if session["user_status"] == ADMIN or session["user_status"] == COACH:
        return render_template('index.html')
    elif session["user_status"] == HEAD:
        return render_template("/instruction_for_head.html")
    elif session["user_status"] == MANAGER:
        return render_template("/instruction_for_manager.html")
    else:
        return redirect("/login")


@app.route("/positions", methods=['POST','GET'])
@login_required
def positions():
    readyStatusList = ['Все', 'Заполнено', 'Не заполнено']
    if request.method == 'GET' and (session["user_status"] == ADMIN or session["user_status"] == COACH):
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
            connection.autocommit = True  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM positions ORDER BY reports_pos ")
                positions = cursor.fetchall()
                #cursor.execute("SELECT * FROM positions WHERE  (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) ORDER BY reports_pos ")
                #positionsNotDone = cursor.fetchall()
                cursor.execute("SELECT DISTINCT reports_pos FROM positions ORDER BY reports_pos")
                headList = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return render_template('positions.html', positions = positions, headList = headList, readyStatusList = readyStatusList, competence = COMPETENCE)

    elif request.method == 'POST' and (session["user_status"] == ADMIN or session["user_status"] == COACH):
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
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name )
            connection.autocommit = True  
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
                    cursor.execute("UPDATE positions SET comp_1 = %(comp_1)s, comp_2 = %(comp_2)s, comp_3 = %(comp_3)s, comp_4 = %(comp_4)s, comp_5 = %(comp_5)s, comp_6 = %(comp_6)s, comp_7 = %(comp_7)s, comp_8 = %(comp_8)s, comp_9 = %(comp_9)s WHERE position_pos = %(position_pos)s and reports_pos = %(mail)s", {'comp_1': comp_1, 'comp_2':comp_2, 'comp_3': comp_3, 'comp_4': comp_4, 'comp_5': comp_5, 'comp_6': comp_6, 'comp_7': comp_7, 'comp_8':comp_8, 'comp_9': comp_9, 'position_pos': position_edit, 'mail': reports_to })
                    flash("Изменения сохранены.")
                    if edit == 'editFromUsers':
                        cursor.execute("SELECT mail FROM users WHERE position = %(position_edit)s AND reports_to = %(reports_to_edit)s", {'position_edit': position_edit, 'reports_to_edit': reports_to_edit})
                        user_mail = cursor.fetchall()
                        return render_template('summary_table.html', user_mail = user_mail[0][0])
                    return redirect('/positions')
                if edit:
                    user_name = request.form.get("user_name")
                    cursor.execute("SELECT * FROM positions WHERE position_pos = %(position_edit)s AND reports_pos = %(reports_to_edit)s", {'position_edit': position_edit, 'reports_to_edit': reports_to_edit})
                    position_edit = cursor.fetchall()
                    if user_name:
                        return render_template('positions.html', position_edit = position_edit, competence = COMPETENCE, editValue = edit, user_name = user_name)
                    else:
                        return render_template('positions.html', position_edit = position_edit, competence = COMPETENCE, editValue = edit)

                


                if search:
                    cursor.execute("SELECT * FROM positions WHERE reports_pos LIKE %(reports_pos)s ORDER BY reports_pos", {'reports_pos': search})
                    positions = cursor.fetchall()
                    return render_template('positions.html', positions = positions, competence = COMPETENCE)
                if reports_to and not ready_status:
                    cursor.execute("SELECT * FROM positions  WHERE reports_pos = %(reports_pos)s ORDER BY reports_pos", {'reports_pos': reports_to})
                    positions = cursor.fetchall()
                elif ready_status and not reports_to:
                    if ready_status == readyStatusList[0]: # all
                        cursor.execute("SELECT * FROM positions ORDER BY reports_pos")
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[1]: # done
                        cursor.execute("SELECT * FROM positions WHERE comp_1 IS NOT NULL AND comp_2 IS NOT NULL AND comp_3 IS NOT NULL AND comp_4 IS NOT NULL AND comp_5 IS NOT NULL AND comp_6 IS NOT NULL AND comp_7 IS NOT NULL AND comp_8 IS NOT NULL AND comp_9 IS NOT NULL ORDER BY reports_pos")
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[2]: # done not
                        cursor.execute("SELECT * FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) ORDER BY reports_pos")
                        positions = cursor.fetchall()
                elif  reports_to and ready_status:
                    if ready_status == readyStatusList[0]: # all
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s ORDER BY reports_pos", {'reports_pos': reports_to})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[1]: # done
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s and comp_1 IS NOT NULL AND comp_2 IS NOT NULL AND comp_3 IS NOT NULL AND comp_4 IS NOT NULL AND comp_5 IS NOT NULL AND comp_6 IS NOT NULL AND comp_7 IS NOT NULL AND comp_8 IS NOT NULL AND comp_9 IS NOT NULL ORDER BY reports_pos", {'reports_pos': reports_to})
                        positions = cursor.fetchall()
                    elif ready_status == readyStatusList[2]: # done not
                        cursor.execute("SELECT * FROM positions WHERE reports_pos = %(reports_pos)s AND (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL OR comp_9 IS NULL) ORDER BY reports_pos" , {'reports_pos': reports_to})
                        positions = cursor.fetchall()
                    
                cursor.execute("SELECT DISTINCT reports_pos FROM positions ORDER BY reports_pos")
                headList = cursor.fetchall()
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        return render_template('positions.html', reports_to_query = reports_to, ready_status_query = ready_status, positions = positions, headList = headList, readyStatusList = readyStatusList, competence = COMPETENCE)
    
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

            return render_template("users.html",headers_list = SORTLIST, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, usereName =usereName, usereMail = usereMail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)

        elif session["user_status"] == HEAD:
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
                        return render_template("questions_for_head.html", allPositionFromList = allPositionFromList, positionFromList = positionFromList, competence = COMPETENCE_DESCRIPTION)
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
        
        elif session['user_status'] == MANAGER:
            print(session['user_status'])
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

                    department = request.form.get("department")
                    reports_to = request.form.get("reports_to")
                    status = request.form.get("status")
                    position  = request.form.get("position")
                    query = request.form.get("query")
                    filtr_sort  = request.form.get("filtr_sort")
                    accept_rules = request.form.get("accept_rules")
                    
                    if accept_rules:
                        print(accept_rules)
                        if accept_rules == 'Приняли':
                            cursor.execute("SELECT * FROM users WHERE accept_rules IS NOT NULL ORDER BY id")
                        elif accept_rules == 'Не приняли':
                            cursor.execute("SELECT * FROM users WHERE accept_rules IS NULL ORDER BY id")
                        users = cursor.fetchall()
                        return render_template("users.html", headers_list = SORTLIST, accept_rules_select = accept_rules, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = STATUS_LIST, positionList = POSITIONS_LIST)


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
                            
                        return render_template("users.html", headers_list = SORTLIST, filtr_sort_position = filtr_sort, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
                       

                    if query:
                        cursor.execute("SELECT * FROM users WHERE mail = %(mail)s ORDER BY id", {'mail': query})
                        users = cursor.fetchall()
                        return render_template("users.html", users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
    
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

            return render_template("users.html", headers_list = SORTLIST, users = users, userDepartment = usereDepartment, usereReports_to = usereReports_to, usereStatus_to = usereStatus_to, userePosition = userePosition, statusList = STATUS_LIST, positionList = POSITIONS_LIST, filtr_department = department, filtr_reports_to = reports_to, filtr_status = status, filtr_position = position)
        
        elif session["user_status"] == HEAD:
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
            print(f'comp: {comp_1}')

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
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
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
            
            return render_template("edit.html", id = id, department = department, reports_to = reports_to, status = status, position = position, name = name, mail = mail, statusList = STATUS_LIST, positionList = POSITIONS_LIST)
        
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
            if  hash: #and (status == ADMIN or status == COACH or status == HEAD):
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
                        if len(pos) == 0 and status != ADMIN and status != COACH:
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
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
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
    if request.method == "POST" and (session["user_status"] == ADMIN or session["user_status"] == COACH):
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
        #if  status == ADMIN or status == COACH or status == HEAD: # and (not hash or checkPassword(hash)):
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
                    if len(pos) == 0 and status != ADMIN and status != COACH:
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
        countErrorManager = 0
        countErrorHead = 0
        countUploadManager = 0
        countUploadHead = 0
        #usersError = []
        #usersUpload = []
        
        # если расширение файла excel, то разбираем файл посточно
        if filename.endswith((".xlsx", ".xls")):
            xlsx = pd.ExcelFile(f'upload_files/{filename}')
            table = xlsx.parse()
            # Подключаемся к базе данных
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True 
                with connection.cursor() as cursor:
                    # Проходип по таблице и записываем сотрудников в базу
                    for i in range(len(table)):
                        # Разбираем данные из считанных строк
                        mail = str(table.iloc[i,:][3]).lower().strip()
                        # Ищем в базе email 
                        cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                        us = cursor.fetchall()
                        # Если существует, то не записываем в базу. Добавляем в список
                        if len(us) != 0:
                            countErrorManager = countErrorManager + 1
                            print(f'не сохранен - {mail}')
                           #usersError = usersError + us
                        # Если нет пользователя в базе, то записываем туда и добавляем в список
                        else:
                            name = str(table.iloc[i,:][2] + ' ' + table.iloc[i,:][1])
                            position = str(table.iloc[i,:][4]).strip()
                            division = str(table.iloc[i,:][5]).strip()
                            department = str(table.iloc[i,:][6]).strip()
                            branch = str(table.iloc[i,:][7]).strip()
                            reports_to = str(table.iloc[i,:][9]).lower().strip()
                            status = MANAGER
                            hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
                            cursor.execute("INSERT INTO users ( name, mail, position, division, department, branch, reports_to, status, hash) VALUES(%(name)s, %(mail)s, %(position)s, %(division)s, %(department)s, %(branch)s, %(reports_to)s, %(status)s, %(hash)s)", {'name': name, 'mail': mail, 'position': position, 'division': division, 'department': department, 'branch': branch, 'reports_to': reports_to, 'status': status, 'hash': hash})
                            countUploadManager = countUploadManager + 1

                            #cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                            #usUpload = cursor.fetchall()
                            #usersUpload = usersUpload + usUpload
                            
                            # Проверяем должность в базе. Если существует, то пропускам
                            cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s AND reports_pos = %(reports_pos)s", {'position': position, 'reports_pos': reports_to})
                            pos = cursor.fetchall()
                            if len(pos) == 0:
                                cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})
                    
                    # Проходип по таблице и записываем руководителей в базу
                    for i in range(len(table)):            
                        mail = str(table.iloc[i,:][9]).lower().strip()
                        cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                        us = cursor.fetchall()
                        # Если пользоватеть существует, то не записываем в базу. Добавляем в список
                        if len(us) != 0:
                            print(f'head did not upload - {mail}')
                            countErrorHead = countErrorHead + 1
                           
                        # Если нет пользователя в базе, то записываем туда и добавляем в список
                        else:
                            division = str(table.iloc[i,:][5]).strip()
                            department = str(table.iloc[i,:][6]).strip()
                            branch = str(table.iloc[i,:][7]).strip()
                            name = str(table.iloc[i,:][8]).strip()
                            reports_to = '-'
                            position = '-'
                            status = HEAD
                            hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
                            cursor.execute("INSERT INTO users ( name, mail, position, division, department, branch, status, hash, reports_to) VALUES(%(name)s, %(mail)s, %(position)s, %(division)s, %(department)s, %(branch)s, %(status)s, %(hash)s, %(reports_to)s)", {'name': name, 'mail': mail, 'position': position, 'division': division, 'department': department, 'branch': branch, 'status': status, 'hash': hash, 'reports_to':reports_to})
                            countUploadHead = countUploadHead + 1
                            

            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
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
                                countErrorManager = countErrorManager + 1
                                usersError = usersError + us
                            else:
                                cursor.execute("INSERT INTO users (department, reports_to, status, position, name, mail, hash) VALUES(%(department)s, %(reports_to)s, %(status)s, %(position)s, %(name)s, %(mail)s, %(hash)s)", {'department': department, 'reports_to': reports_to, 'status': status, 'position': position, 'name': name, 'mail': mail, 'hash': hash})
                                countUploadManager = countUploadManager + 1
                                cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                                usUpload = cursor.fetchall()
                                usersUpload = usersUpload + usUpload
                                cursor.execute("SELECT * FROM positions WHERE position_pos = %(position)s", {'position': position})
                                pos = cursor.fetchall()
                                if len(pos) == 0 and status != ADMIN and status != COACH:
                                    cursor.execute("INSERT INTO positions (position_pos, reports_pos) VALUES(%(position_pos)s, %(reports_pos)s)", {'position_pos': position, 'reports_pos': reports_to})



                except Exception as _ex:
                    print("[INFO] Error while working with PostgresSQL", _ex)
                    flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                    return redirect('/')
                finally:
                    if connection:
                        connection.close()
                        print("[INFO] PostgresSQL connection closed")                  

        else:
            flash('Тип загруженного файла не поддерживается.')
            return redirect('/')
        
        flash(f"Загруженно {countUploadManager} пользователей и {countUploadHead} руководителей.")
        return redirect ('/users')
        # не самый красивый вариант
        #return render_template('afterUpload.html', countError = countError, countUpload = countUpload, usersError = usersError, usersUpload = usersUpload)
    
    else:
        return redirect('/')


@app.route('/test_results', methods=['POST', 'GET'])
@login_required
def test_results():
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
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
        return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST_SMALL)
    

    if request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
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
            return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST)
        
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
            return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST_SMALL)

        elif user_mail:
            print(user_mail)
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
                 return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST_SMALL, from_summary = from_summary)
            else:
                return render_template('/test_results.html', testResults = testResults, headerList = HEADER_LIST_FROM_TEST_SMALL)

    else:
        return redirect('/test_results')


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
                        mail = str(table.iloc[i,:][2]).strip()
                        cursor.execute("SELECT * FROM test_results WHERE mail = %(mail)s", {'mail': mail})
                        user_result = cursor.fetchall()
                        if len(user_result) == 0:
                            name_test = str(table.iloc[i,:][0]).strip()
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

                            cursor.execute("INSERT INTO test_results (name_test, mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management) VALUES (%(name_test)s, %(mail)s, %(reliability)s, 	%(discipline)s, 	%(executive)s, 	%(responsibility)s, 	%(resolved)s, 	%(organizational)s, 	%(software)s, 	%(adaptation)s, 	%(planning)s, 	%(page)s, 	%(strengthening)s, 	%(building_on_achievements)s, 	%(building_for_development)s, 	%(innovation)s, 	%(approved)s, 	%(loyalty)s, 	%(currency)s, 	%(country)s, 	%(preparedness_for_compromise)s, 	%(cooperation)s, 	%(openness)s, 	%(openness_of_feedback)s, 	%(clientoority)s, 	%(customer_needs_orientation)s, 	%(partnership)s, 	%(adoption_of_decisions)s, 	%(systemic_thinking)s, 	%(business)s, 	%(forward_thinking)s, 	%(effective_communication)s, 	%(clean_communication)s, 	%(impunity_and_influence)s, 	%(negotiations)s, 	%(cross_functional_interaction)s, 	%(informal_leadership)s, 	%(management)s, 	%(implementation_management)s, 	%(motivation_of_subordinates)s, 	%(organization_of_work)s, 	%(change_management)s, 	%(development_of_subordinates)s, 	%(command_management)s)", {'name_test': name_test, 'mail': mail, 'reliability': reliability, 	'discipline': discipline, 	'executive': executive, 	'responsibility': responsibility, 	'resolved': resolved, 	'organizational': organizational, 	'software': software, 	'adaptation': adaptation, 	'planning': planning, 	'page': page, 	'strengthening': strengthening, 	'building_on_achievements': building_on_achievements, 	'building_for_development': building_for_development, 	'innovation': innovation, 	'approved': approved, 	'loyalty': loyalty, 	'currency': currency, 	'country': country, 	'preparedness_for_compromise': preparedness_for_compromise, 	'cooperation': cooperation, 	'openness': openness, 	'openness_of_feedback': openness_of_feedback, 	'clientoority': clientoority, 	'customer_needs_orientation': customer_needs_orientation, 	'partnership': partnership, 	'adoption_of_decisions': adoption_of_decisions, 	'systemic_thinking': systemic_thinking, 	'business': business, 	'forward_thinking': forward_thinking, 	'effective_communication': effective_communication, 	'clean_communication': clean_communication, 	'impunity_and_influence': impunity_and_influence, 	'negotiations': negotiations, 	'cross_functional_interaction': cross_functional_interaction, 	'informal_leadership': informal_leadership, 	'management': management, 	'implementation_management': implementation_management, 	'motivation_of_subordinates': motivation_of_subordinates, 	'organization_of_work': organization_of_work, 	'change_management': change_management, 	'development_of_subordinates': development_of_subordinates, 	'command_management': command_management})
                            countUpload = countUpload + 1

                        else: 
                            countError = countError + 1

            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")
            flash(f"Загруженно {countUpload} результатов тестирования. Не загружено {countError} результатов тестирования.")
            return redirect ('/test_results')

    else:
        return redirect ('/')


@app.route('/mail_heads', methods = ['GET', 'POST'])
@login_required
def mail_heads():
    # создаем списки и счетчики отправленных и неотправленных сообщений
    notSendList = []
    counterSend = 0
    counterNotSend = 0
    # Статусы для фильтра 
    readyStatusList = ['Все', 'Отправлено', 'Не отправлено']
    # Флаг для выбора пути. Одно письмо, всем или токо тем, кто еще не получал приглашение
    flag  = request.form.get('flag')

    
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        # Выбираем все пользователей со статусом HEAD  и все почты для поиска
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':HEAD})
                users = cursor.fetchall()
                cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': HEAD})
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

    elif request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        reports_to = request.form.get('reports_to')
        ready_status = request.form.get('ready_status')
        search = request.form.get('search')

        # Данные для фитра и поиска
        if reports_to or ready_status or search:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': HEAD})
                    headList = cursor.fetchall()

                    if reports_to and not ready_status:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s  and mail = %(reports_to)s ORDER BY id", {'status':HEAD, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif ready_status and not reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date NOT LIKE '-' ORDER BY id", {'status':HEAD})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date = '-' ORDER BY id", {'status':HEAD})
                            users = cursor.fetchall()
                        else:
                            return redirect('/mail_heads')
                    elif ready_status and reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date NOT LIKE '-' AND mail = %(reports_to)s ORDER BY id", {'status':HEAD, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date = '-' AND mail = %(reports_to)s ORDER BY id", {'status':HEAD, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        else:
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail = %(reports_to)s ORDER BY id", {'status':HEAD, 'reports_to': reports_to})
                            users = cursor.fetchall()
                    elif search:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail = %(search)s ORDER BY id", {'status':HEAD, 'search': search})
                        users = cursor.fetchall()
        
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/mail_heads')            
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")

            return render_template('mail.html', users = users, headList = headList, readyStatusList = readyStatusList, reports_to_query = reports_to, ready_status_query = ready_status)        
                
        # if single send mode
        if flag == 'single':
            user_name = request.form.get('user_name')
            user_mail = request.form.get('user_mail')
            try:
                # create date, password and message
                today = datetime.date.today()
                user_password = createPassword()
                hash = generate_password_hash(user_password, "pbkdf2:sha256")
                msg = Message('From STI-Partners', recipients=[user_mail])
                #msg.body = (f'Welcom to 123.com.\nYour login {user_mail}\nYour password {user_password}')
                msg.body = render_template("to_head_email.txt", user_name = user_name, user_mail = user_mail, user_password = user_password)
                msg.html = render_template("to_head_email.html", user_name = user_name, user_mail = user_mail, user_password = user_password)
                mail.send(msg)
    
                # update database
                try:
                    connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                    connection.autocommit = True
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                except Exception as _ex:
                    print(f'[INFO] Error while working PostgresSQL', _ex)
                    flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                    return redirect('/')
                    
                finally:
                    if connection:
                        connection.close()
                        print("[INFO] PostgresSQL nonnection closed")
                flash(f'Приглашение отправлено')
                print(f'[INFO] Message has bin sent via mail sender.')
                return redirect('/mail_heads')

            except Exception as _ex:
                flash("Сообщение не отправлено. Проверьте коректно ли указана электронная почта.")
                print(f'[INFO] Error while working mail sender', _ex)
                return redirect('/mail_heads')

        elif flag == 'all_invite':
            today = today = datetime.date.today()
            try: 
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    #cursor.execute("SELECT name, mail  FROM users WHERE status = %(status)s", {'status': HEAD})
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':HEAD})
                    users = cursor.fetchall()
                    for singleUser in users:
                        try:
                            user_password = createPassword()
                            hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                            msg = Message("From STI-Partners", recipients=[singleUser[5]])
                            msg.body = render_template("to_head_email.txt", user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            msg.html = render_template('to_head_email.html', user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            mail.send(msg)
                            counterSend = counterSend + 1
                            cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':singleUser[5]})
                            print(f'[INFO] Message has bin sent via mail sender.')
                        except Exception as _ex:
                            notSendList.append(singleUser)
                            counterNotSend = counterNotSend + 1 
                            print(f'[INFO] Error while working mail sender:', _ex)
                        
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':HEAD})
                    users = cursor.fetchall()
                            
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
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
            return render_template('mail.html', users = users, notSendList = notSendList)

        elif flag == 'has_not_invite':
            today = today = datetime.date.today()
            try: 
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    # default value mail_date is -
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail_date IS NULL", {'status':HEAD})
                    users = cursor.fetchall()
                    for singleUser in users:
                        try:
                            user_password = createPassword()
                            hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                            msg = Message("From STI-Partners", recipients=[singleUser[5]])
                            msg.body = render_template("to_head_email.txt", user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            msg.html = render_template('to_head_email.html', user_name = singleUser[4], user_mail = singleUser[5], user_password = user_password)
                            mail.send(msg)
                            counterSend = counterSend + 1
                            cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':singleUser[5]})
                            print(f'[INFO] Message has bin sent via mail sender.')
                        except Exception as _ex:
                            notSendList.append(singleUser)
                            counterNotSend = counterNotSend + 1 
                            print(f'[INFO] Error while working mail sender:', _ex)

                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':HEAD})
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
            return render_template('mail.html', users = users, notSendList = notSendList)

    elif request.method == 'POST' and session['user_status'] == HEAD:
        # сообщение от пользователя в конце опросника
        if flag == 'mail_from_head_end':
            message_from_head = request.form.get('messege_from_head')
            if message_from_head:  
                try:
                    head_mail = session['user_mail']
                    head_name = session['user_name']
                    msg = Message("From Burusan's project", recipients=[HEAD_COACH_EMAIL])
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
                    msg = Message("From Burusan's project", recipients=[HEAD_COACH_EMAIL])
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
    if request.method == 'GET':
        return render_template('/reset_password.html')

    elif request.method == 'POST':
        user_name = request.form.get('username')
        if user_name:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    # Проверка на существование пользователя
                    cursor.execute("SELECT mail, name, status FROM users WHERE mail = %(mail)s", {'mail': user_name})
                    us = cursor.fetchall()
                    status = us[0][2]
                    if len(us) == 1: #and (status == COACH or status == ADMIN or status == HEAD):
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
                            return render_template('reset_password.html')

                        cursor.execute("UPDATE users SET hash = %(hash)s WHERE mail = %(mail)s", {'hash': hash, 'mail': user_name})
                        flash('Проверьте свою электронную почту. Если ваш email зарегистрирован в систему, то вы получите письмо с данными для входа.')
                        return render_template('/login.html')

                    else:
                        flash('Проверьте свою электронную почту. Если ваш email зарегистрирован в систему, то вы получите письмо с данными для входа.')
                        return render_template('/login.html')

            except Exception as _ex:
                print("[INFO] Error while working with PostgresSQL", _ex)
                flash("В процессе создания запроса произошла ошибка. Пожалуйста, обновите страницу и повторите попытку.")
                return render_template('reset_password.html')
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL connection closed")
        else:
            flash('Укажите адрес электронной почты и повторите запрос')
            return redirect('reset_password')

    else:
        return redirect('/')


@app.route('/summary', methods = ['GET', 'POST'])
@login_required
def summary():
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        allManagers = []
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
            with connection.cursor() as cursor:
                # Данные все пользователей
                cursor.execute("SELECT id, name, mail, department, position, reports_to, status FROM users")
                usersData = cursor.fetchall()
                #print(usersData)

                for userData in usersData:
                    #print(f'userData = {userData[6]}')
                    if userData[6] == 'manager':
                        # Важнейшие компетенции
                        cursor.execute("SELECT comp_1, comp_2, comp_3, comp_4, comp_5,comp_6, comp_7, comp_8, comp_9 FROM positions WHERE reports_pos = %(reports_to)s AND position_pos = %(position)s", {'reports_to': userData[5], 'position': userData[4]})
                        topCompetence = cursor.fetchall()
                        #print(f'topCompetence - {topCompetence}' )
                        
                        # Результаты тестирования
                        cursor.execute("SELECT reliability, organizational, strengthening, approved, country, clientoority, adoption_of_decisions, effective_communication, management FROM test_results WHERE mail = %(userMail)s", {'userMail': userData[2]})
                        testResults = cursor.fetchall() 
                        #print(f'testResults - {testResults}')

                        # Если нет результатов тестирования
                        if len(testResults) == 0:
                            testResults.append((0,0,0,0,0,0,0,0,0))
                        
                        # общий словарь
                        summaryDict = {}
                        for i in range(9):
                            summaryDict[f'comp_{i+1}'] = (HEADER_LIST_FROM_TEST_SMALL[i], topCompetence[0][i], testResults[0][i])
                        
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

                        # Список по конкретному пользователю
                        manager = [userData[1], userData[2]]
                        # Сравнить первые 5 компетенций их с результатами тестов
                        for i in range(5):
                            # Сравнить ранж с результатом теста
                            if summaryDict[newCompRang[i]][1] == None:
                                manager.append('-')
                            elif summaryDict[newCompRang[i]][1] <= 3 and summaryDict[newCompRang[i]][1] >= 1 and summaryDict[newCompRang[i]][2] <= 70:
                                manager.append(summaryDict[newCompRang[i]][0])
                            elif summaryDict[newCompRang[i]][1] <= 6 and summaryDict[newCompRang[i]][1] >= 4 and summaryDict[newCompRang[i]][2] <= 30:
                                manager.append(summaryDict[newCompRang[i]][0])
                            else:
                                manager.append('-')
                            
                                

                      
                        # Список списоков
                        allManagers.append(manager)
                        
                        
                        #print(f'userData - {userData};\n\nsummaryDict - {summaryDict};\n\nnewCompRang - {newCompRang}\n\n\n {allManagers}')
                   

        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")

        # Передаем данные для создания страницы        
        return render_template('/summary_table_all_managers.html',  allManagers = allManagers)

    elif request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        # почта запрашиваемого пользователя
        userMail = request.form.get('userMail')
        # Если запрос пришел из общей сводной таблицы
        fromAllTAble = request.form.get('fromAllTable')

        # Подключение к базе данных
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True  
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
                    summaryDict[f'comp_{i+1}'] = (HEADER_LIST_FROM_TEST_SMALL[i], topCompetence[0][i], testResults[0][i])
                
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

    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        # Выбираем все пользователей со статусоv MANAGER  и все почты для поиска
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status': MANAGER})
                users = cursor.fetchall()
                cursor.execute("SELECT DISTINCT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': MANAGER})
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

    elif request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        reports_to = request.form.get('reports_to')
        ready_status = request.form.get('ready_status')
        search = request.form.get('search')

        # Данные для фитра и поиска
        if reports_to or ready_status or search:
            try:
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT mail FROM users WHERE status = %(status)s ORDER BY mail", {'status': MANAGER})
                    headList = cursor.fetchall()

                    if reports_to and not ready_status:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s  and mail = %(reports_to)s ORDER BY id", {'status':MANAGER, 'reports_to': reports_to})
                        users = cursor.fetchall()
                    elif ready_status and not reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date NOT LIKE '-' ORDER BY id", {'status':MANAGER})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date = '-' ORDER BY id", {'status':MANAGER})
                            users = cursor.fetchall()
                        else:
                            return redirect('/mail_manager')
                    elif ready_status and reports_to:
                        if ready_status == 'Отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date NOT LIKE '-' AND mail = %(reports_to)s ORDER BY id", {'status':MANAGER, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        elif ready_status == 'Не отправлено':
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s AND mail_date = '-' AND mail = %(reports_to)s ORDER BY id", {'status':MANAGER, 'reports_to':reports_to})
                            users = cursor.fetchall()
                        else:
                            cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail = %(reports_to)s ORDER BY id", {'status':MANAGER, 'reports_to': reports_to})
                            users = cursor.fetchall()
                    elif search:
                        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail = %(search)s ORDER BY id", {'status':MANAGER, 'search': search})
                        users = cursor.fetchall()
        
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
                flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                return redirect('/mail_manager')            
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgresSQL nonnection closed")

            return render_template('mail_manager.html', users = users, headList = headList, readyStatusList = readyStatusList, reports_to_query = reports_to, ready_status_query = ready_status)        
               
         # if single send mode
        if flag == 'single':
            user_name = request.form.get('user_name')
            user_mail = request.form.get('user_mail')
            try:
                # create date, password and message
                today = datetime.date.today()
                user_password = createPassword()
                hash = generate_password_hash(user_password, "pbkdf2:sha256")
                msg = Message('From STI-Partners', recipients=[user_mail])
                
                msg.body = render_template("to_manager_email.txt", user_name = user_name, user_mail = user_mail, user_password = user_password)
                msg.html = render_template("to_manager_email.html", user_name = user_name, user_mail = user_mail, user_password = user_password)
                mail.send(msg)
    
                # update database
                try:
                    connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                    connection.autocommit = True
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                except Exception as _ex:
                    print(f'[INFO] Error while working PostgresSQL', _ex)
                    flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
                    return redirect('/')
                    
                finally:
                    if connection:
                        connection.close()
                        print("[INFO] PostgresSQL nonnection closed")
                flash(f'Приглашение отправлено')
                print(f'[INFO] Message has bin sent via mail sender.')
                return redirect('/mail_manager')

            except Exception as _ex:
                flash("Сообщение не отправлено. Проверьте коректно ли указана электронная почта.")
                print(f'[INFO] Error while working mail sender', _ex)
                return redirect('/mail_manager')

        elif flag == 'all_invite':
            today = today = datetime.date.today()
            try: 
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':MANAGER})
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
                        
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':MANAGER})
                    users = cursor.fetchall()
                            
            except Exception as _ex:
                print(f'[INFO] Error while working PostgresSQL', _ex)
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

        elif flag == 'has_not_invite':
            today = today = datetime.date.today()
            try: 
                connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
                connection.autocommit = True
                with connection.cursor() as cursor:
                    # default value mail_date is -
                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s and mail_date IS NULL", {'status':MANAGER})
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

                    cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date FROM users WHERE status = %(status)s ORDER BY id", {'status':MANAGER})
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

    elif request.method == 'POST' and session['user_status'] == MANAGER:
        # сообщение от пользователя в конце опросника
        # сообщение от пользователя в начале опросника
        if flag == 'mail_from_manager_start':
            message_from_manager = request.form.get('messege_from_manager')
            if message_from_manager:  
                try:
                    head_mail = session['user_mail']
                    head_name = session['user_name']
                    msg = Message("From Burusan's project", recipients=[HEAD_COACH_EMAIL])
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


@app.route('/accept_rules', methods = ['GET', 'POST'])
@login_required
def accept_rules():
    if request.method == 'GET' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, accept_rules FROM users WHERE status = %(status)s ORDER BY id", {'status': MANAGER})
                users = cursor.fetchall()
               
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
            flash('Не удалось подключиться к базе данных. Попробуйте повторить попытку.')
            return redirect('/')
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")
        return render_template('accept_rules.html', users = users)


    elif request.method == 'POST' and (session['user_status'] == ADMIN or session['user_status'] == COACH):
            pass
    else:
        return redirect('/')


#CREATE TABLE users (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY NOT NULL, department VARCHAR(50), reports_to VARCHAR(50), status VARCHAR(50), position VARCHAR(50), name VARCHAR(50), mail VARCHAR(50) UNIQUE, hash VARCHAR(50));
#CREATE TABLE users (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY NOT NULL, department VARCHAR(150), reports_to VARCHAR(150), status VARCHAR(150), position VARCHAR(150), name VARCHAR(150), mail VARCHAR(150) UNIQUE, hash VARCHAR(300), mail_date VARCHAR(50), division VARCHAR(150), branch VARCHAR(150), accept_rules VARCHAR(50));
#CREATE TABLE positions (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, position_pos VARCHAR(50), reports_pos VARCHAR(50), comp_1 INTEGER, comp_2 INTEGER, comp_3 INTEGER, comp_4 INTEGER, comp_5 INTEGER, comp_6 INTEGER, comp_7 INTEGER, comp_8 INTEGER, comp_9 INTEGER);
#CREATE TABLE test_results (ID INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, name_test VARCHAR(50), mail VARCHAR(50), reliability INTEGER,	discipline INTEGER,	executive INTEGER,	responsibility INTEGER,	resolved INTEGER,	organizational INTEGER,	software INTEGER,	adaptation INTEGER,	planning INTEGER,	page INTEGER,	strengthening INTEGER,	building_on_achievements INTEGER,	building_for_development INTEGER,	innovation INTEGER,	approved INTEGER,	loyalty INTEGER,	currency INTEGER,	country INTEGER,	preparedness_for_compromise INTEGER,	cooperation INTEGER,	openness INTEGER,	openness_of_feedback INTEGER,	clientoority INTEGER,	customer_needs_orientation INTEGER,	partnership INTEGER,	adoption_of_decisions INTEGER,	systemic_thinking INTEGER,	business INTEGER,	forward_thinking INTEGER,	effective_communication INTEGER,	clean_communication INTEGER,	impunity_and_influence INTEGER,	negotiations INTEGER,	cross_functional_interaction INTEGER,	informal_leadership INTEGER,	management INTEGER,	implementation_management INTEGER,	motivation_of_subordinates INTEGER,	organization_of_work INTEGER,	change_management INTEGER,	development_of_subordinates INTEGER, command_management INTEGER);
#INSERT INTO test_results (mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management ) VALUES ('123@ed.er1' , 4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,34,4,4,4,44,4,4,4,4,4,44);
#INSERT INTO test_results (mail , reliability , discipline , executive , responsibility , resolved , organizational , software , adaptation , planning , page , strengthening  , building_on_achievements  , building_for_development  , innovation  , approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , organization_of_work  , change_management  , development_of_subordinates  , command_management ) VALUES ('123@ed.er2' , 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42);