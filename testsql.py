
import csv
from fileinput import nextfile
with open("upload_files/123321.csv", newline='') as file:
    x = csv.reader(file, delimiter=';', quotechar='|', skipinitialspace=True)
    next(x)
    for i in x:
        print(i[0])
        #print(', '.join(i))



   

  
