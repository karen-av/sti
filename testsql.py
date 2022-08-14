
from config import func_sql

name  = 'karen'

x = '"SELECT * FROM users = %(name)s", {"name": name};'
func_sql(x)
