from flask import Flask, render_template
from flask_mail import Message, Mail
from threading import Thread
import psycopg2
from config import Config, host, user, password, db_name
from werkzeug.security import generate_password_hash
import datetime
from helpers import createPassword


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)


def asyncc(f):
    def wrapper(*args, **kwargs):
        Thread(target = f, args = args, kwargs = kwargs).start()
    return wrapper


def message_sender(subject, text_body, html_body, user_name, user_mail, user_password):
    msg = Message(subject,  recipients = [user_mail])
    msg.body = render_template(text_body, user_name = user_name, user_mail = user_mail, user_password = user_password)
    msg.html = render_template(html_body, user_name = user_name, user_mail = user_mail, user_password = user_password)
    mail.send(msg)
    

@asyncc
def send_message_manager(status):
    with app.app_context():
        today = datetime.date.today()
        try: 
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules \
                                FROM users WHERE status = %(status)s ORDER BY id", {'status':status})
                users = cursor.fetchall()
                for singleUser in users:
                    subject = "Проект «Развитие компетенций сотрудников back-office»"
                    user_name = singleUser[4]
                    user_mail = singleUser[5]
                    user_password = createPassword()
                    hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                    if singleUser[6] != None and singleUser[7] == None and singleUser[6] != str(today): 
                        text_body = "reminder_to_manager.txt"
                        html_body = 'reminder_to_manager.html'
                        message_sender(subject, text_body, html_body, user_name, user_mail, user_password)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                            WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail}) 
                    elif singleUser[6] == None:
                        text_body = "to_manager_email.txt"
                        html_body = 'to_manager_email.html'
                        message_sender(subject, text_body, html_body, user_name, user_mail, user_password)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                        WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                                                        
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")


# переписать для руководителей и Удалить
@asyncc
def send_message(subject, text_body, html_body, user_name, user_mail, user_password):
    with app.app_context():
        hash  = generate_password_hash(user_password, "pbkdf2:sha256")
        today = datetime.date.today()
        try:
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True 
            with connection.cursor() as cursor:
                msg = Message(subject,  recipients = [user_mail])
                msg.body = render_template(text_body, user_name = user_name, user_mail = user_mail, user_password = user_password)
                msg.html = render_template(html_body, user_name = user_name, user_mail = user_mail, user_password = user_password)
                mail.send(msg)
                cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
        except Exception as _ex:
            print(f'[INFO]: {_ex}')
        finally:
            if connection:
                connection.close()