
import psycopg2

host = "ec2-34-193-44-192.compute-1.amazonaws.com"
user = "vmfxqzwglzoagi"
password = "8c83f577e40db85b6e810dfa0935f79f41f32c4c2414c89a9fa31f28957bf786"
db_name = "dc2k8sqsffd92a"
port = 5432


class Config(object):
    SECRET_KEY = "12345"
    DEBAG = True
    TESTING = False
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    #app.config['MAIL_DEBUG'] = True
    MAIL_USERNAME = 'backoffice@sti-partners.ru'
    MAIL_PASSWORD = 'jz4V4$?9RpiGzVG'
    MAIL_DEFAULT_SENDER = 'backoffice@sti-partners.ru'
    MAIL_MAX_EMAILS = None
    #app.config['MAIL_SUPPRESS_SEND'] = False
    MAIL_ASCII_ATTACHMENTS = False
    RECAPTCHA_PUBLIC_KEY = "6LdYqogiAAAAAGj1Hqg_jUIg9iJYXPEXU58ERyCs"
    RECAPTCHA_PRIVATE_KEY = "6LdYqogiAAAAAAH8VMkBb8Dd9qSPxS2rfVRWr2H8"
    RECAPTCHA_DISABLE = True #  будет капча или нет
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = 'upload_files'
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem" 


def func_sql(comand):
    try:
        # connect to exist database
        connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
        connection.autocommit = True
        #insert data to table
        with connection.cursor() as cursor:
            cursor.execute(comand)
            print(cursor.fetchall())

    except Exception as _ex:
        print("[INFO] Error while working with PostgresSQL", _ex)
    finally:
        if connection:
            connection.close()

