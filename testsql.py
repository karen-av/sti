
import psycopg2
from config import func_sql, host, user, password, db_name

name  = 'karen'
x = "SELECT * FROM users = %s', (name, ));"
func_sql(x)
