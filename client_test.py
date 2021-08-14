import requests
import pprint
import json
user = {'userid': '', 'password': ''}  # plz type ur id&pass
user['userid']=input('id>>')
user['password']=input('pass>>')
#r = requests.post("https://manabaunko.azurewebsites.net/timetable", data=user) #POST user data
r = requests.post("http://127.0.0.1:8000", data=json.dumps(user)) #POST user data
#http://127.0.0.1:5000/

pprint.pprint(r.json())
#