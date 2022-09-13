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

def connection_db():
    connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
    return connection


def message_sender(text_body, html_body, user_name, user_mail, user_password):
    msg = Message("Проект «Развитие компетенций сотрудников back-office»",  recipients = [user_mail])
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
                    user_name = singleUser[4]
                    user_mail = singleUser[5]
                    user_password = createPassword()
                    hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                    if singleUser[6] != None and singleUser[7] == None and singleUser[6] != str(today): 
                        text_body = "reminder_to_manager.txt"
                        html_body = 'reminder_to_manager.html'
                        message_sender(text_body, html_body, user_name, user_mail, user_password)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                            WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail}) 
                    elif singleUser[6] == None:
                        text_body = "to_manager_email.txt"
                        html_body = 'to_manager_email.html'
                        message_sender(text_body, html_body, user_name, user_mail, user_password)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                        WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                                                        
        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")


@asyncc
def send_message_head(status):
    with app.app_context():
        today = datetime.date.today()
        try: 
            connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT department, reports_to, status, position, name, mail, mail_date \
                                FROM users WHERE status = %(status)s AND mail in \
                                (SELECT reports_pos FROM positions WHERE (comp_1 IS NULL OR comp_2 IS NULL OR comp_3 IS NULL \
                                    OR comp_4 IS NULL OR comp_5 IS NULL OR comp_6 IS NULL OR comp_7 IS NULL OR comp_8 IS NULL \
                                    OR comp_9 IS NULL))\
                                ORDER BY id", {'status':status})
                users = cursor.fetchall()
                for singleUser in users:
                    user_name = singleUser[4]
                    user_mail = singleUser[5]
                    user_password = createPassword()
                    hash  = generate_password_hash(user_password, "pbkdf2:sha256")
                    if singleUser[6] != None and singleUser[6] != str(today): 
                        text_body = "reminder_to_head.txt"
                        html_body = 'reminder_to_head.html'
                        message_sender(text_body, html_body, user_name, user_mail, user_password) 
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                        WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})
                    elif singleUser[6] == None:
                        text_body = "to_head_email.txt"
                        html_body = 'to_head_email.html'
                        message_sender(text_body, html_body, user_name, user_mail, user_password)
                        cursor.execute("UPDATE users SET hash = %(hash)s, mail_date = %(date)s \
                                        WHERE mail = %(mail)s", {'hash': hash, 'date': today, 'mail':user_mail})

        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)
        finally:
            if connection:
                connection.close()
                print(f"[INFO] PostgresSQL nonnection closed")


@asyncc
def upload_test_results(table):
    with app.app_context():
        try:
            connection = connection_db()
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

                        cursor.execute(
                                        "INSERT INTO test_results (name_test, mail , reliability , discipline , executive , \
                                        responsibility , resolved , organizational , software , adaptation , planning , page , \
                                        strengthening  , building_on_achievements  , building_for_development  , innovation  , \
                                        approved  , loyalty  , currency  , country  , preparedness_for_compromise  , cooperation  , \
                                        openness  , openness_of_feedback  , clientoority  , customer_needs_orientation  , partnership  , \
                                        adoption_of_decisions  , systemic_thinking  , business  , forward_thinking  , effective_communication  , \
                                        clean_communication  , impunity_and_influence  , negotiations  , cross_functional_interaction  , \
                                        informal_leadership  , management  , implementation_management  , motivation_of_subordinates  , \
                                        organization_of_work  , change_management  , development_of_subordinates  , command_management) \
                                        VALUES (%(name_test)s, %(mail)s, %(reliability)s, 	%(discipline)s, 	%(executive)s, 	%(responsibility)s, \
                                        %(resolved)s, 	%(organizational)s, 	%(software)s, 	%(adaptation)s, 	%(planning)s, 	%(page)s, 	\
                                        %(strengthening)s, 	%(building_on_achievements)s, 	%(building_for_development)s, 	%(innovation)s, 	\
                                        %(approved)s, 	%(loyalty)s, 	%(currency)s, 	%(country)s, 	%(preparedness_for_compromise)s, 	\
                                        %(cooperation)s, 	%(openness)s, 	%(openness_of_feedback)s, 	%(clientoority)s, 	%(customer_needs_orientation)s, \
                                        %(partnership)s, 	%(adoption_of_decisions)s, 	%(systemic_thinking)s, 	%(business)s, 	%(forward_thinking)s, 	\
                                        %(effective_communication)s, 	%(clean_communication)s, 	%(impunity_and_influence)s, 	%(negotiations)s, 	\
                                        %(cross_functional_interaction)s, 	%(informal_leadership)s, 	%(management)s, 	%(implementation_management)s, 	\
                                        %(motivation_of_subordinates)s, 	%(organization_of_work)s, 	%(change_management)s, 	%(development_of_subordinates)s, 	\
                                        %(command_management)s)", \
                                        {'name_test': name_test, 'mail': mail, 'reliability': reliability, 	'discipline': discipline, 	\
                                        'executive': executive, 	'responsibility': responsibility, 	'resolved': resolved, 	'organizational': organizational, 	\
                                        'software': software, 	'adaptation': adaptation, 	'planning': planning, 	'page': page, 	'strengthening': strengthening, 	\
                                        'building_on_achievements': building_on_achievements, 	'building_for_development': building_for_development, 	\
                                        'innovation': innovation, 	'approved': approved, 	'loyalty': loyalty, 	'currency': currency, 	'country': country, \
                                        'preparedness_for_compromise': preparedness_for_compromise, 	'cooperation': cooperation, 	'openness': openness, 	\
                                        'openness_of_feedback': openness_of_feedback, 	'clientoority': clientoority, 	'customer_needs_orientation': customer_needs_orientation, \
                                        'partnership': partnership, 	'adoption_of_decisions': adoption_of_decisions, 	'systemic_thinking': systemic_thinking, \
                                        'business': business, 	'forward_thinking': forward_thinking, 	'effective_communication': effective_communication, \
                                        'clean_communication': clean_communication, 	'impunity_and_influence': impunity_and_influence, 	'negotiations': negotiations, \
                                        'cross_functional_interaction': cross_functional_interaction, 	'informal_leadership': informal_leadership, 	'management': management, \
                                        'implementation_management': implementation_management, 	'motivation_of_subordinates': motivation_of_subordinates, \
                                        'organization_of_work': organization_of_work, 	'change_management': change_management, 	'development_of_subordinates': development_of_subordinates, \
                                        'command_management': command_management}
                                        )

        except Exception as _ex:
            print(f'[INFO] Error while working PostgresSQL', _ex)               
        finally:
            if connection:
                connection.close()



@asyncc
def upload_file_users(table, manager_status, head_status):
    with app.app_context():
        try:
            connection = connection_db()
            connection.autocommit = True 
            with connection.cursor() as cursor:
                # Проходип по таблице и записываем сотрудников в базу
                for i in range(len(table)):
                    # Разбираем данные из считанных строк
                    mail = str(table.iloc[i,:][3]).lower().strip()
                    # Ищем в базе email 
                    cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                    us = cursor.fetchall()
                    # # Если нет пользователя в базе, то записываем туда и добавляем в список
                    if len(us) == 0:
                        name = str(table.iloc[i,:][2] + ' ' + table.iloc[i,:][1])
                        position = str(table.iloc[i,:][4]).strip()
                        division = str(table.iloc[i,:][5]).strip()
                        department = str(table.iloc[i,:][6]).strip()
                        branch = str(table.iloc[i,:][7]).strip()
                        reports_to = str(table.iloc[i,:][9]).lower().strip()
                        status = manager_status
                        hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
                        cursor.execute(
                                        "INSERT INTO users ( name, mail, position, division, department, branch, reports_to, status, hash) \
                                        VALUES(%(name)s, %(mail)s, %(position)s, %(division)s, %(department)s, %(branch)s, %(reports_to)s, %(status)s, %(hash)s)", \
                                        {'name': name, 'mail': mail, 'position': position, 'division': division, 'department': department, 'branch': branch, \
                                            'reports_to': reports_to, 'status': status, 'hash': hash}
                                        )
                        # Проверяем должность в базе. Если существует, то пропускам
                        cursor.execute(
                                        "SELECT * FROM positions WHERE position_pos = %(position)s \
                                        AND reports_pos = %(reports_pos)s", \
                                        {'position': position, 'reports_pos': reports_to}
                                        )
                        pos = cursor.fetchall()
                        if len(pos) == 0:
                            cursor.execute(
                                            "INSERT INTO positions (position_pos, reports_pos) \
                                            VALUES(%(position_pos)s, %(reports_pos)s)", \
                                            {'position_pos': position, 'reports_pos': reports_to}
                                            )
                # Проходип по таблице и записываем руководителей в базу
                for i in range(len(table)):            
                    mail = str(table.iloc[i,:][9]).lower().strip()
                    cursor.execute("SELECT * FROM users WHERE mail = %(mail)s", {'mail': mail})
                    us = cursor.fetchall()
                    # Если нет пользователя в базе, то записываем туда и добавляем в список
                    if len(us) == 0:
                        division = str(table.iloc[i,:][5]).strip()
                        department = str(table.iloc[i,:][6]).strip()
                        branch = str(table.iloc[i,:][7]).strip()
                        name = str(table.iloc[i,:][8]).strip()
                        reports_to = '-'
                        position = '-'
                        status = head_status
                        hash = generate_password_hash(createPassword(), "pbkdf2:sha256")
                        cursor.execute(
                                        "INSERT INTO users ( name, mail, position, division, department, branch, status, hash, reports_to) \
                                        VALUES(%(name)s, %(mail)s, %(position)s, %(division)s, %(department)s, %(branch)s, %(status)s, %(hash)s, %(reports_to)s)", \
                                        {'name': name, 'mail': mail, 'position': position, 'division': division, \
                                            'department': department, 'branch': branch, 'status': status, 'hash': hash, 'reports_to':reports_to}
                                        )
        except Exception as _ex:
            print("[INFO] Error while working with PostgresSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgresSQL connection closed")  