import string
from webbrowser import open_new
from flask import Flask
from flask import request
import json

import neo_user
import kmeans
import mssql

def save_cities_sql(cities_df):
    cities = []
    for index, row in cities_df.iterrows():
        cities.append(row["all_cities"])
        mssql.create_city_table_sqldb(cities)
  
def load_data():
    try:
        mssql.create_hobby_lobby_database()
        cities_df = kmeans.pd.read_csv("cities.csv", low_memory = False)
        save_cities_sql(cities_df)
        kmeans.kmeansclustering()
    except Exception as e:
        print(f"Error during load_data: {e}")
    
# Setup flask server
app = Flask(__name__)


@app.route('/login', methods = ['POST'])
def fetch_users():
    try:
        print("hi1")
        users = mssql.fetch_users_sql()
        print("users:", users)
        user_list = [{'usernum': usernum, 'password': data['password'], 'email': data['email']} for usernum, data in users.items()]
        print(user_list)
        return json.dumps(user_list)
    except Exception as e:
        print("Error fetching users:", e)
        return json.dumps([])  # Return empty list in case of an error
 
    
@app.route('/clusterusers/<int:usernum>', methods=['GET'])
def fetch_cluster_by_user(usernum):
    try:
        users = neo_user.get_cluster_users(usernum)
        filtered_users = list()
        for u in users:
            user_details_dict = {
                "usernum": u['m']["user_num"],
                "name": u['m']["name"],
                "surname": u['m']["surname"],
                "gender": u['m']["gender"],
                "date_of_birth": u['m']["date_of_birth"],
                "city": u['m']["city"],
                "hobby": u['m']["hobby"]
                }
            print(u['m']['user_num'])
            filtered_users.append(user_details_dict)
        print(filtered_users)
        return json.dumps(filtered_users)
    except Exception as e:
        print("Error fetching users:", e)
        return json.dumps([]) 


@app.route('/fetch_all_users/<int:usernum>',methods=['GET'])
def fetch_all_users(usernum):
    try:
        users = neo_user.get_all_other_users(usernum)
        print("---fetch_all_users----", users)
        filtered_users = list()
        for u in users:
            user_details_dict = {
                "usernum": u['n']["user_num"],
                "name": u['n']["name"],
                "surname": u['n']["surname"],
                "gender": u['n']["gender"],
                "date_of_birth": u['n']["date_of_birth"],
                "city": u['n']["city"],
                "hobby": u['n']["hobby"]
                }
            print(u['n']['user_num'])
            filtered_users.append(user_details_dict)
        print(filtered_users)
        return json.dumps(filtered_users)
    except Exception as e:
        print("Error fetching users:", e)
        return json.dumps([]) 
    
    
@app.route('/user/<int:usernum>', methods=['GET'])
def fetch_user_details(usernum):
    try:
        print(usernum)
        user_details = neo_user.get_user_details_from_neo(usernum)
        user_details_dict = {
            "usernum": user_details["u"]["user_num"],
            "name": user_details["u"]["name"],
            "surname": user_details["u"]["surname"],
            "gender": user_details["u"]["gender"],
            "date_of_birth": user_details["u"]["date_of_birth"],
            "city": user_details["u"]["city"],
            "hobby": user_details["u"]["hobby"]
        }
        print("user_details_dict:", user_details_dict)
        return json.dumps(user_details_dict)
    except Exception as e:
        print("Error fetching user details for profile:", e)
        return json.dumps({})  # Return empty object in case of an error

@app.route('/cities', methods = ['GET'])
def fetch_cities():
    cities = mssql.fetch_cities_sql()
    cities.sort()
    return json.dumps(cities)

@app.route('/hobbies', methods = ['POST'])
def fetch_hobbies():
    unsorted_hobbies = mssql.fetch_hobbies_sql()
    sorted_hobbies = dict(sorted(unsorted_hobbies.items()))
    print(sorted_hobbies)
    return json.dumps(sorted_hobbies)

@app.route('/adduser', methods = ['POST'])
def add_user():
    user = request.json
    print(user)
    email = user["email"]
    password = user["pwd"]
    new_user_data = {
        "name": user["firstname"],
        "surname": user["surname"],
        "gender": user["gender"],
        "dob": user["dob"],
        "city": user["city"],
        "hobbies":user["hobbies"]
    }
    if(mssql.check_if_email_exists_sql(email)):
        print("user with this email already exists")
        return json.dumps("It seems like you already have an account with this email addrress. Try to login.")
    result_neo = neo_user.add_user_to_neo4j(new_user_data)
    if(result_neo==None):
        print("failed to save user in neo")
        return json.dumps("We encountered a problem. Please try again later.")
    result_sql = mssql.save_new_user_sqldb(result_neo,email,password)
    if(result_sql==False):
        neo_user.delete_node(result_neo)
        print("failed to save user in sql")
        return json.dumps("We encountered a problem. Please try again later.")
    print("--------------------------------------------")
    print(result_neo)
    kmeans.kmeansclustering()
    print("added users to clusters")
    return json.dumps("success")

@app.route('/updateuser', methods = ['POST'])
def update_user():
    user = request.json
    print("user:", user)
    if(user["which_form"] == "updatePasswordEmail"):
        if(mssql.check_if_other_user_exists_sql(user["email"],int(user["usernum"])) ):
            return json.dumps("user with this email already exists")
        result_sql = mssql.update_user_sqldb(int(user["usernum"]), user["email"],user["pwd"])
        if(result_sql==False):
            return json.dumps("failed to update user in sql")
        else:
            print("--------------------------------------------")
            print(result_sql)
            return json.dumps("successfully updated user")
    if(user["which_form"] == "updateOtherDetails"):
        update_user_data = {
            "name": user["name"],
            "surname": user["surname"],
            "user_num": int(user["usernum"]),
            "gender": user["gender"],
            "date_of_birth": user["date_of_birth"],
            "city": user["city"],
            "hobby":user["hobby"],
        }
        print(update_user_data)
        result_neo = neo_user.update_user_neo(update_user_data)
        print(result_neo)
        if(result_neo==None):
            return json.dumps("failed to update user in neo")
        else:
            return json.dumps("successfully updated user")
    else:
        return json.dumps("Error! failed to update user")
       

@app.route('/fetchUserDetailsFromSSQL/<int:usernum>', methods = ['GET'])
def fetchUserFromSSQL(usernum):
    try:
         print(usernum)
         user = mssql.fetch_user_sql(usernum)
         print("---fetched user----", user)   
         return json.dumps(user) 
    except Exception as e:
        print("Error in fetchUserFromSSQL:", e)
        return json.dumps(e) 
        

@app.route('/searchByExactHobby/<int:usernum>/<string:queryStr>', methods=['GET'])
def search_by_exact_hobby(usernum, queryStr):
    try:
        print(usernum, queryStr)
        users = neo_user.get_users_with_hobby(usernum, queryStr, 'exact')  # Pass 'exact' as the search method
        print("---search_by_exact_hobby----", users)
        filtered_users = list()
        for user in users:
            user_details_dict = {
                "usernum": user["user_num"],
                "name": user["name"],
                "surname": user["surname"],
                "gender": user["gender"],
                "date_of_birth": user["date_of_birth"],
                "city": user["city"],
                "hobby": user["hobby"]
            }
            print(user['user_num'])
            filtered_users.append(user_details_dict)
        print(filtered_users)
        return json.dumps(filtered_users)
    except Exception as e:
        print("Error in search_by_exact_hobby:", e)
        return json.dumps([])

@app.route('/searchByOrHobby/<int:usernum>/<string:queryStr>', methods=['GET'])
def search_by_or_hobby(usernum, queryStr):
    try:
        print(usernum, queryStr)
        users = neo_user.get_users_with_hobby(usernum, queryStr, 'or')  # Pass 'or' as the search method
        print("---search_by_or_hobby----", users)
        filtered_users = list()
        for user in users:
            user_details_dict = {
                "usernum": user["user_num"],
                "name": user["name"],
                "surname": user["surname"],
                "gender": user["gender"],
                "date_of_birth": user["date_of_birth"],
                "city": user["city"],
                "hobby": user["hobby"]
            }
            print(user['user_num'])
            filtered_users.append(user_details_dict)
        print(filtered_users)
        return json.dumps(filtered_users)
    except Exception as e:
        print("Error in search_by_or_hobby:", e)
        return json.dumps([])


@app.route('/addFriend/<int:usernum>/<int:friendnum>', methods=['GET'])
def add_friend(usernum, friendnum):
    try:
        neo_user.add_friend(usernum,friendnum);
        return json.dumps("successfully added friend")
    except Exception as e:
            print("Error in adding friends:", e)
            return json.dumps([])


@app.route('/removeFriend/<int:usernum>/<int:friendnum>', methods=['GET'])
def remove_friend(usernum, friendnum):
    try:
        neo_user.remove_friend(usernum,friendnum);
        return json.dumps("successfully removed friend")
    except Exception as e:
            print("Error in adding friends:", e)
            return json.dumps([])


@app.route('/checkFriend/<int:usernum>/<int:friendnum>', methods=['GET'])
def check_friend(usernum, friendnum):
    try:
        return json.dumps(neo_user.check_friend(usernum,friendnum))
    except Exception as e:
            print("Error in adding friends:", e)
            return json.dumps([])


@app.route('/getFriends/<int:usernum>', methods=['GET'])
def get_friends(usernum):
    try:
        users = neo_user.get_all_friends(usernum)
        filtered_users = list()
        for u in users:
            user_details_dict = {
                "email": mssql.fetch_user_sql(u['f']["user_num"])["email"],
                "usernum": u['f']["user_num"],
                "name": u['f']["name"],
                "surname": u['f']["surname"],
                "gender": u['f']["gender"],
                "date_of_birth": u['f']["date_of_birth"],
                "city": u['f']["city"],
                "hobby": u['f']["hobby"]
                }
            filtered_users.append(user_details_dict)
        print(filtered_users)
        return json.dumps(filtered_users)
    except Exception as e:
            print("Error in adding friends:", e)
            return json.dumps([])

if __name__ == "__main__":
    #load_data()
    app.run(host="0.0.0.0",port=5000)

    

    
