import main
from flask import Flask, jsonify, abort, make_response, request
import os
import sys
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized

PATH = os.path.abspath('')
sys.path.append(PATH)


app = Flask(__name__)


@app.route("/", methods=["POST"])
def manaba():
    #{'userid': "ID" ,'password': "PASSWORD"}
    userid = request.form['userid']
    password = request.form['password']
    return jsonify(main.app(userid, password))

@app.route("/")
def method_error():
    #{'userid': "ID" ,'password': "PASSWORD"}
    return jsonify('405')
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


if __name__ == "__main__":
    app.run()