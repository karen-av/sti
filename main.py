
import psycopg2
from config import func_sql, host, user, password, db_name

try:
    # connect to exist database
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )
    connection.autocommit = True

    # the cursor for perfoming database operations
    #cursor = connection.cursor()

    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        print(f"Server version: {cursor.fetchone()}")

    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS test(id serial PRIMARY KEY, f_name varchar(50) NOT NULL, username varchar(50) NOT NULL);")
        #connection.commit()
        print(f"[INFO] Table created successfully")
    
    #insert data to table
    with connection.cursor() as cursor:
        #cursor.execute("INSERT INTO test(f_name, username) VALUES('Oledgd', 'user_oleg');")
        #name = 'Oleg'
        #cursor.execute("SELECT * FROM test WHERE f_name = %s'", (name, ));
        #cursor.execute("SELECT * FROM test WHERE f_name = %(name)s", {'name': name });

        cursor.execute("SELECT * FROM test WHERE f_name = 'Oleg';")
        print(cursor.fetchone())


except Exception as _ex:
    print("[INFO] Error while working with PostgresSQL", _ex)
finally:
    if connection:
        #cursor.close()
        connection.close()
        print("[INFO] PostgresSQL connection closed")

name = 'Oleg'
#cursor.execute("SELECT * FROM test WHERE f_name = %s'", (name, ));

#x = "SELECT * FROM test WHERE f_name = 'Olegd';"
#func_sql("SELECT * FROM test WHERE f_name = %(name)s", {'name': 'Oleg' })
func_sql("SELECT * FROM test WHERE f_name = 'Olegd';")
