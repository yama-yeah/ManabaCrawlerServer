import requests
import pprint
user = {'userid': '', 'password': ''}  # plz type ur id&pass
user['userid']=input('id>>')
user['password']=input('pass>>')
user['except_id']=[]
#r = requests.post("https://manabaunko.azurewebsites.net/timetable", data=user) #POST user data
r = requests.post("http://127.0.0.1:5000/timetable", json=user,headers={'Content-Type': 'application/json'}) #POST user data
#http://127.0.0.1:5000/
pprint.pprint(r.json())
#pprint.pprint(r.json()['timetable']['Thu'])
#