from manaba import Manaba
from fastapi import FastAPI
import os
import sys
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized
import uvicorn
from pydantic import BaseModel
PATH = os.path.abspath('')
sys.path.append(PATH)


app = FastAPI()
#app.config['JSON_AS_ASCII'] = False


class User(BaseModel):
    userid: str
    password: str


@app.get("/")
def hello():
    #{'userid': "ID" ,'password': "PASSWORD"}
    return 'hello you must to post user infomation'


@app.get("/timetable")
def hellotime():
    #{'userid': "ID" ,'password': "PASSWORD"}
    return 'hello you must to post user infomation'


@app.post("/")
def sub(user: User):
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = user.userid
    password = user.password
    manaba = Manaba(userid, password)
    return manaba.get_tasks()


@app.post("/timetable")
def time(user: User):
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = user.userid
    password = user.password
    manaba = Manaba(userid, password)
    return manaba.get_timetable()


if __name__ == "__main__":
    uvicorn.run(app)
