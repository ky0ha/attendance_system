import sqlite3, os
from functools import wraps

os.chdir("./出勤系统")

class Database(object):
    __instance = None
    
    def __new__(self, *args, **kwargs):
        if Database.__instance == None:
            Database.__instance = super().__init__(self, *args, **kwargs)
        else:
            raise ValueError("Cannot create multiple jects with a singleton class.")
        return Database.__instance
    
    def __init__(self, database: str = "attendance_system"):
        # self.connect(database)
        # self.cursor = self.db.cursor()
        self.database = database
        self.struct_map = {
            "teacher": "(tname)",
            "student": "(sname)",
            "course": "(cname, credit)",
            "period": "(sno, cno, tno, period, record_time)"
        }
    
    def connect(self):
        self.db = sqlite3.connect(self.database)
        return self.db.cursor()
    
    def save_close(self):
        self.db.commit()
        self.db.close()
    
    # @staticmethod
    # def __open_wraper(func):
    #     @wraps(func)
    #     def open_save(*args, **kwargs):
    #         db = sqlite3.connect("attendance_system")
            
    #         result = func(*args, **kwargs)
            
    #         db.commit()
    #         db.close()
    #         return result
    #     return open_save
    
    # @__open_wraper
    def recovery(self):
        with open("init.sql", encoding="utf-8") as f:
            sql_script = f.read()
        
        cursor = self.connect()
        cursor.executescript(sql_script)
        self.save_close()
    
    # @__open_wraper
    def insert(self, *values, table: str):
        if len(values)==1:
            temp_values = f"('{values[0]}')"
        else:
            temp_values = f"{values}"
        
        sql_command = f"INSERT INTO {self.struct_map[table]} values {temp_values};"
        
        cursor = self.connect()
        cursor.execute(sql_command)
        self.save_close()
    
    def select(self, sname):
        sql_command = f"SELECT period.record_no, student.sname, course.cname, teacher.tname, course.credit, period.record_time FROM period JOIN student ON period.sno = student.sno JOIN teacher ON period.tno = teacher.tno JOIN course ON period.cno = course.cno WHERE student.sname = '{sname}';"

        cursor = self.connect()
        data = cursor.fetchall()
        self.save_close()
        return data
    
    def delete(self, record_no):
        sql_command = f"DELETE FROM period where record_no={record_no}"
        
        cursor = self.connect()
        cursor.execute(sql_command)
        self.save_close()