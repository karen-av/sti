import datetime
from config import host, user, password, db_name
import psycopg2

manager = 'manager'
today = datetime.date.today()
counterSend = 0
counterNotSend = 0
notSendList = []

try: 
    connection = psycopg2.connect(host = host, user = user, password = password, database = db_name)
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SELECT department, reports_to, status, position,  name,  mail, mail_date, accept_rules FROM users WHERE status = %(status)s ORDER BY id", {'status':manager})
        users = cursor.fetchall()
        for singleUser in users:
            if singleUser[6] != None:
                if singleUser[7] == None and singleUser[6] != str(today):
                    counterSend += 1
                    print(f'send - {singleUser[6]} - {singleUser[7]}')
                else:
                    notSendList.append(singleUser)
                    counterNotSend += 1   
                    print(f'not - {singleUser[6]} - {singleUser[7]}')
            else:
                counterNotSend += 1
                print('not invite')  
except Exception as _ex:
    print(f'[INFO] {_ex}')
finally:
    if connection:
        connection.close()

yesterday = '2022-09-08'
today_1 = '2022-09-12'
print(f'today - {today}\nyesterday - {yesterday}\ntoday_1 - {today_1}')
if str(today) == yesterday:
    print("GO")
elif str(today) == today_1:
    print("GO_2")
