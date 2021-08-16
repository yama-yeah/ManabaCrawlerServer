from manaba import Manaba
from flask import Flask, jsonify, abort, make_response, request
import os
import sys
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized
PATH = os.path.abspath('')
sys.path.append(PATH)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/")
def hello():
    #{'userid': "ID" ,'password': "PASSWORD"}
    return jsonify('hello you must to post user infomation')


@app.route("/timetable")
def hellotime():
    #{'userid': "ID" ,'password': "PASSWORD"}
    return jsonify('hello you must to post user infomation')


@app.route("/", methods=["POST"])
def sub():
    #{'userid': "ID" ,'password': "PASSWORD"}
    keys = request.form.keys()
    userid = request.form['userid']
    password = request.form['password']
    least = '%void%'
    exception_id = ['%void%']
    if('least' in keys):
        least = request.form['least']
    if('exception_id' in keys):
        exception_id = request.form['exception_id']
    manaba = Manaba(userid, password)
    return jsonify(manaba.get_tasks(exception_id, least))


@app.route("/timetable", methods=["POST"])
def time():
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = request.form['userid']
    password = request.form['password']
    manaba = Manaba(userid, password)
    return jsonify(manaba.get_timetable())


if __name__ == "__main__":
    app.run(debug=True)

'''
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
    '''
