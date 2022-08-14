
import psycopg2

host = "ec2-34-193-44-192.compute-1.amazonaws.com"
user = "vmfxqzwglzoagi"
password = "8c83f577e40db85b6e810dfa0935f79f41f32c4c2414c89a9fa31f28957bf786"
db_name = "dc2k8sqsffd92a"
port = 5432

def func_sql(comand):
    try:
        # connect to exist database
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )
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

