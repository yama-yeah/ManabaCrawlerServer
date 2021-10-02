import re
from manaba import Manaba
from flask import Flask, json, jsonify, abort, make_response, request
import os
import sys
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized
import ast
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
    json = request.get_json()
    keys=json.keys()
    userid = json['userid']
    password = json['password']
    least = '%void%'
    except_id = ['%void%']
    except_type = []
    if('least' in keys):
        least = json['least']
    if('except_id' in keys):
        except_id=json['except_id']
        #except_id = ast.literal_eval(_id_list)
    if('except_type' in keys):
        _tasktype_list=json['except_type']
        except_type = ast.literal_eval(_tasktype_list)
    manaba = Manaba(userid, password)
    #return request.get_data()
    return jsonify(manaba.get_tasks( except_id=except_id,least=least,except_type=except_type))


@app.route("/timetable", methods=["POST"])
def time():
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = request.json['userid']
    password = request.json['password']
    manaba = Manaba(userid, password)
    return jsonify(manaba.get_timetable())

@app.route('/login',methods=['POST'])
def login():
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = request.json['userid']
    password = request.json['password']
    manaba = Manaba(userid, password)
    status={'status':''}
    if(manaba.check_login()):
        status['status']='success'
    else:
        status['status']='failed'
    return jsonify(status)

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
