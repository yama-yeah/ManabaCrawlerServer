import requests
import pprint
user = {'userid': '', 'password': ''}  # plz type ur id&pass
user['userid']=input('id>>')
user['password']=input('pass>>')
r = requests.post("https://manabaunko.azurewebsites.net:5000", data=user) #POST user data
pprint.pprint(r.json())
