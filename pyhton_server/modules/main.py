USER_NUM = 0
import string
from flask import Flask # work with nodeks
from flask import request
import json 
#
import neo_user
import kmeans
import create_data
import mssql

# Setup flask server
app = Flask(__name__)


@app.route('/arraysum', methods = ['POST']) 
def sum_of_array(): 
    data = request.get_json() 
    print(data)
  
    # Data variable contains the 
    # data from the node server
    ls = data['array'] 
    result = sum(ls) # calculate the sum
  
    # Return data in json format 
    return json.dumps({"result":result})

"""
@app.route('/send_data', methods = ['POST'])
    def send_data():
    result = get_users_from_neo()
    print(result)
    return json.dumps(result)
"""
@app.route('/add', methods = ['POST'])
def add_user():
    user = request.json
    print(user)
    # Data variable contains the 
    # data from the node server
    #user = json.load(user)
    email = user["email"]
    password = user["password"]
    firstname = user["firstname"]
    surname = user["surname"]
    gender = user["gender"]
    dob = user["dob"]
    city = user["city"]
    hobby1 = user["hobby1"]
    hobby2 = user["hobby2"]
    hobby3 = user["hobby3"]
    print(email,password,firstname)
    result = neo_user.save_new_user_in_neo(firstname,surname,gender,dob,city,hobby1,hobby2,hobby3)

    print("--------------------------------------------")
    print(result)
    print("--------------------------------------------")
    print(json.dumps(result))
    return json.dumps(result)


@app.route('/cities', methods = ['POST'])
def fetch_cities():
    unsorted_cities = mssql.fetch_cities_sql()
    sorted_cities = dict(sorted(unsorted_cities.items()))
    print(sorted_cities)
    return json.dumps(sorted_cities)


@app.route('/hobbies', methods = ['POST'])
def fetch_hobbies():
    unsorted_hobbies = mssql.fetch_hobbies_sql()
    sorted_hobbies = dict(sorted(unsorted_hobbies.items()))
    print(sorted_hobbies)
    return json.dumps(sorted_hobbies)

if __name__ == "__main__":
    kmeans.predict_data()
    app.run(port=5000)
    #print("success")
    #neo_user.get_user_from_neo(2)
    #create_data.create_data()
    #get_cluster_users_from_neo(10)