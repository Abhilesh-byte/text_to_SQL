import sqlite3

## Connect to sqlite
connection=sqlite3.connect("student.db")

## Create a curosr object to insert record,create table,retrieve
cursor=connection.cursor()

## create the table
table_info="""
Create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),
SECTION VARCHAR(25),MARKS INT);

"""

cursor.execute(table_info)

## Insert some more records
cursor.execute("INSERT INTO STUDENT VALUES('Ravi','10th','A',90)")
cursor.execute("INSERT INTO STUDENT VALUES('Ramesh','10th','A',80)")
cursor.execute("INSERT INTO STUDENT VALUES('Suresh','10th','A',70)")
cursor.execute("INSERT INTO STUDENT VALUES('Mahesh','10th','A',60)")
cursor.execute("INSERT INTO STUDENT VALUES('Rajesh','10th','A',50)")
cursor.execute("INSERT INTO STUDENT VALUES('Rakesh','10th','A',40)")
cursor.execute("INSERT INTO STUDENT VALUES('Rohit','10th','A',30)")
cursor.execute("INSERT INTO STUDENT VALUES('Rohini','10th','A',20)")
cursor.execute("INSERT INTO STUDENT VALUES('Rohit','10th','A',10)")
cursor.execute("INSERT INTO STUDENT VALUES('Rohini','10th','A',0)")

# print instert records are
print("Records inserted succesfully")

data = cursor.execute("SELECT * FROM STUDENT")

for row in data:
    print(row)

# close the connection
connection.commit()
connection.close()