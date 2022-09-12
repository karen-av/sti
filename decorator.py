from flask import Flask, render_template
from flask_mail import Message, Mail
from threading import Thread
import psycopg2
from config import Config, host, user, password, db_name
from werkzeug.security import generate_password_hash
import datetime



app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

def asyncc(f):
    def wrapper(*args, **kwargs):
        Thread(target = f, args = args, kwargs = kwargs).start()
    return wrapper


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
                cursor.execute("UPDATE users_new SET hash = %(hash)s, mail_date = %(date)s \
                                                    WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                print(f'sent - {user_mail}')
        except Exception as _ex:
            print(f'[INFO]: {_ex}')
        finally:
            if connection:
                connection.close()