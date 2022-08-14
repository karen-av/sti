import csv
from cs50 import SQL

db = SQL("sqlite:///sti.db")

with open('upload_files/111.csv') as f:
    #print(f.readlines())
    dr = csv.DictReader(f)
    for i in dr:
        print(i['\ufeff'])
    
    



    
