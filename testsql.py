import csv
from cs50 import SQL

db = SQL("sqlite:///sti.db")

with open('upload_files/users.csv', newline="") as csvfile:
    spam = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for s in spam:
        name = (s[0]+' ' +s[1])
        print(name)
        


    #print(f.readlines())
    #dr = csv.DictReader(f)
    #for i in dr:
     #   print(i['\ufeff'])
    
   


    
