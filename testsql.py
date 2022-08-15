
from config import func_sql

import string 
import secrets


symbols = ['!@#$%&?-+=~']
num = 10
res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(num)) 
print(res)

  
