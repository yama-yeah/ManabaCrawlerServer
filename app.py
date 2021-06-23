import main
from flask import Flask, jsonify, abort, make_response, request
import os
import sys
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized
PATH = os.path.abspath('')
sys.path.append(PATH)


app = Flask(__name__)




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
    userid = request.form['userid']
    password = request.form['password']
    return jsonify(main.app(userid, password,"sub"))
@app.route("/timetable", methods=["POST"])
def time():
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = request.form['userid']
    password = request.form['password']
    return jsonify(main.app(userid, password,"time"))
'''
@app.errorhandler(NotFound)
def page_not_found_handler(e: HTTPException):
    return jsonify('404')


@app.errorhandler(Unauthorized)
def unauthorized_handler(e: HTTPException):
    return jsonify('401')


@app.errorhandler(Forbidden)
def forbidden_handler(e: HTTPException):
    return jsonify('403')


@app.errorhandler(RequestTimeout)
def request_timeout_handler(e: HTTPException):
    return jsonify('408')
'''

if __name__ == "__main__":
    app.run()
