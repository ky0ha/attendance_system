import sqlite3, os

os.chdir("./出勤系统")

db = sqlite3.connect("attendance_system")
cursor = db.cursor()
cursor.execute("INSERT INTO teacher (tname) values ('test');")
db.commit()
print(cursor)