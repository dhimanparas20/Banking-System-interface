from flask_restful import Resource, Api
from flask import render_template
from dotenv import load_dotenv
from datetime import datetime
from os import system,environ
from time import sleep
from flask import *
import json,time
import requests
import pymongo
import random 

# Downloads the Config.env file
CONFIG_FILE_URL = environ.get('CONFIG_FILE_URL')
try:
    if len(CONFIG_FILE_URL) == 0:
        raise TypeError
    try:
        res = rget(CONFIG_FILE_URL)
        if res.status_code == 200:
            with open('config.env', 'wb+') as f:
                f.write(res.content)
        else:
            log_error(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        log_error(f"CONFIG_FILE_URL: {e}")
except:
    pass       
  
# Loading Config Vars from Config.env file
load_dotenv('config.env', override=True)
def getConfig(name: str):
    return environ[name]
 
HEROKU_APP_NAME = ""
HEROKU_APP_NAME = getConfig("HEROKU_APP_NAME")

#Connecting to the  client local/cloud.
client = pymongo.MongoClient("mongodb://localhost:27017/")
'''client = pymongo.MongoClient("mongodb+srv://<username>:<password>@cluster1.n5hitou.mongodb.net/?retryWrites=true&w=majority")'''
print(client)

#Creating a collection/datafield
db = client["MST-Bank"]  #name of DB
collection = db['User-DB'] # name of collection

#Clear the terminal output
system("clear")

# Genrating API for the User
def gen_api():
  lower = "abcdefghijklmnopqrstuvwxyz"
  upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  number = "0123456789"
  all = lower + upper + number 
  api= "".join(random.sample(all, 15))
  return (api)

# Generate account number for user
def gen_accno():
  number = "01234567890123456789"
  acc_no= ''.join(random.sample(number, 13))
  return (int(acc_no))

# Get date time
def get_time():
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  return (dt_string)	

app = Flask(__name__)
api = Api(app)

#Main Home Page
class Home(Resource):
  def get(self):
    print("--------------------------")
    print("Home Page loaded") 
    return make_response(render_template('index.html'))
  
#Registeration page    
class register(Resource):
  def get(self):
    print("--------------------------")
    print("registeration Page loaded") 
    return make_response(render_template('register.html')) 
  
#Registeration done
class register_done(Resource):
  def post(self):
    email = request.form.get('email')
    name = request.form.get('name')
    psw = request.form.get('pass')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    data = collection.find_one({"email":email})
    try:
      if email == data['email']:
        print("-------------------------")
        print("Email alredy exists.")
        return {"Message":f"Email: {email} alredy exists Please try again","OR":f"Goto the Login Page {HEROKU_APP_NAME}/login"},202
        #return make_response(render_template('register.html'))
    except:  
      dict = {"name":name,"dob":dob,"email":email,"passwd":psw,"gender":gender,"API":gen_api(),
              "accno":gen_accno(),"balance":100,"status":"No Current Transactions","lastdate":None}
      collection.insert_one(dict)
      print("--------------------------------------")
      print("Data Added Sucessfully to DataBase.")
      return make_response(render_template('index.html'),200)
        
  def get(self):
    print("--------------------------")
    print("registeration Page loaded") 
    return make_response(render_template('register.html'),200)

#Login page   
class login(Resource):
  def get(self):
    print("--------------------------")
    print("Login Page loaded") 
    return make_response(render_template('login.html')) 

#After Login Welcome page =) login done.
class welcome(Resource):
  def post(self):
    email = request.form.get('email')
    psw = request.form.get('psw')
    data = collection.find_one({"email":email,"passwd":psw},{"_id":0})
    try:
      if email == data['email'] and psw == data['passwd']:
        print("--------------------------")
        print(f"Welcome Page for {data['name']} loaded/Login Done")  
        return make_response(render_template('welcome.html',name=data['name'],dob=data['dob'],accno=data['accno'],
                                             balance=data['balance'],time=get_time(),api=data['API'],msg=data['status'],
                                             lastdate=data['lastdate'],url=HEROKU_APP_NAME))
        '''return [{"name":data['name'],"dob":data['dob'],"email":data['email'],"api":data['API'],"Date and time":get_time()},
                {"account_no":data['accno'],"balance":data['balance']},
                {"message":"Please use the above generated API. Keep it safe and do not share it with anyone.",
                "usage":"use site address +/api and add json or params as you wish as a callback Query."}]
        '''        
    except:  
      print("--------------------------")
      print("Invalid password")
      return make_response(render_template('login.html'))
    
  def get(self):
    print("--------------------------")
    print("Login First")
    return make_response(render_template('login.html'))

#Forgot password page  
class forgotpass(Resource):
  def get(self):
    print("---------------------------------")
    print("password reset help Page loaded")  
    return {"Message":"Please Contact Your Bank or Message us at https://www.t.me/Ken_kaneki_69 ","OR":"Telegram us @Ken_kaneki_69"},200  
  
# Sending money
class send_money(Resource):
  def get(self):
    print("---------------------------------")
    print("Sending Money Page loaded")  
    return make_response(render_template('send_money.html'))
              
# Sending money done
class send_money_done(Resource):
  def post(self):
    api = request.form.get('api')
    accno = request.form.get('accno')
    amtt = request.form.get('amt')
    amt = int(amtt)
    data1 = collection.find_one({"API":api})
    data2 = collection.find_one({"accno":int(accno)})
    try:
      balance1 = data1['balance']
      balance2 = data2['balance']
      if balance1 >= amt :
        updata1 = {"$set":{"balance":balance1-amt,"status":f"Sent Rs.{amt} to {data2['name']}","lastdate":get_time()}}
        collection.update_one({"API":api},updata1)
        updata2 = {"$set":{"balance":balance2+amt,"status":f"received Rs.{amt} from {data1['name']}","lastdate":get_time()}}
        collection.update_one({"accno":int(accno)},updata2)
        data3 = collection.find_one({"API":api})
        print("--------------------------")
        print(f"Money Sent Sucessfully by for {data1['name']}") 
        return {"Message":f"Money Sent Sucessfully to Mr./Ms. {data2['name']}","old balance balance":data1['balance'],
                "current balance":data3['balance'],"Date time":get_time()},200
      else:
        print("--------------------------")
        print("Low balance")
        return {"your current balance":balance1,"Amount your want to send":amt,"Message":"Lesser funds than Required Amount."},202   
    except:  
      print("--------------------------")
      print("Invalid API or Acc No.")
      return{"Api You typed":api,"receivers account no you typed":accno,"Message":"Please RECHECK the acc no or api and try again"},404

#Reset User's API 
class reset_api(Resource):
  def get(self):
    print("---------------------------------")
    print("Reset API Page loaded")  
    return make_response(render_template('reset_api.html',url=HEROKU_APP_NAME))
  
# Reset API Done  
class reset_api_done(Resource):
  def post(self):
    print("---------------------------------")
    print("Reset API Done Page loaded")
    api = request.form.get('api')
    accno = request.form.get('accno')
    try:
      data = collection.find_one({"API":api,"accno":int(accno)})
      new_api = gen_api()
      updata = {"$set":{"API":new_api}}
      collection.update_one({"API":api},updata) 
      data2 = collection.find_one({"API":new_api,"accno":int(accno)})
      print("------------------------------")
      print("Api Changed") 
      return {"Name":data['name'],"old_API":data['API'],"new_API":data2['API'],"Date and Time":get_time(),"Message":"Api Changed"},200  
    except:
      print("---------------------------------")
      print("Api not Changed")
      return {"api entered":api,"Acc. No. entered":accno,"Message":"Invalid details.Please check the api or account no and try again"},404
    
#Returning api Call
class apii(Resource):
  def get(self):
    try:
      #n1 = request.form.get('api')  this is for form method
      n1 = request.json['api']
      print(n1)
    except:  
      n1 = request.args.get('api')
      print(n1)
    one = collection.find_one({"API":n1})   
    print(one)
    try:
      if n1 == one['API']:
        return {"name":one['name'],"email":one['email'],"api":one['API']},200
    except:
      return {"error":"No such APi/User found. Please Register first"},400   
        
# Adding Valid Routes    
api.add_resource(Home, '/',methods=['GET', 'POST'])
api.add_resource(register, '/register',methods=['GET', 'POST'])
api.add_resource(register_done, '/register_done',methods=['GET', 'POST'])
api.add_resource(login, '/login',methods=['GET', 'POST'])
api.add_resource(welcome, '/welcome',methods=['GET', 'POST'])
api.add_resource(forgotpass, '/forgot_pass',methods=['GET', 'POST'])
api.add_resource(send_money, '/send_money',methods=['GET', 'POST'])
api.add_resource(send_money_done, '/send_money/done',methods=['GET', 'POST'])
api.add_resource(reset_api, '/reset_api',methods=['GET', 'POST'])
api.add_resource(reset_api_done, '/reset_api_done',methods=['GET', 'POST'])
api.add_resource(apii, '/api',methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)