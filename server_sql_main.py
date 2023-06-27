from fastapi import *
import pymysql
from pymysql.constants import CLIENT

host="localhost"
user="sign_in"
passwd="becaegbbe013599!"
dbname='daily_sign'
client_flag = CLIENT.MULTI_STATEMENTS

app = FastAPI()

@app.get("/api/mysql/sender")
def sql_sender(command: str):
    with pymysql.connect(host=host, user=user, passwd=passwd, database=dbname, client_flag=client_flag) as db:
        cursor = db.cursor()
        cursor.execute(command)
        result = cursor.fetchall()
    return {'result': result}

@app.post("/api/mysql/sender")
def sql_senter(command: str):
    with pymysql.connect(host=host, user=user, passwd=passwd, database=dbname, client_flag=client_flag) as db:
        cursor = db.cursor()
        try:
            cursor.execute(command)
            db.commit()
        except:
            return {'result': -1}
    return {'result': 1}