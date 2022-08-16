
import pandas as pd




u = pd.read_excel("upload_files/111.xlsx")


xlsx = pd.ExcelFile("upload_files/111.xlsx")
table = xlsx.parse()
l = len(table)
print(l)

for i in range(l):
    department = table.iloc[i,:][0]
    report_to = table.iloc[i,:][1]
    position = table.iloc[i,:][2]
    status = table.iloc[i,:][3]
    name = table.iloc[i,:][4]
    mail = table.iloc[i,:][5]
    hash = table.iloc[i,:][6]
    xxx = table.iloc[i,:][7]
    
    print(department, report_to, status, name, mail, hash, xxx)
    
    

  
