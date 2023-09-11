import main # main module of the application
from main import string # libarary that enables working with strings
import random
import numpy as np
import pandas as pd
import time # we don't use it - should we remove it?
import datetime
import mssql


def get_data():
    # this function reads a csv file, and returns names, genders, surnames, citis, regions, hobbies and hobby categories. 
    data = pd.read_csv("hobbies_data.csv", low_memory=False)
    names_genders = data[["Name", "Gender"]]
    surnames = data["Surnames"].dropna() # dropna() drops all rows with null values.
    cities_regions = data[["Cities", "Regions"]].dropna()
    hobbies = data["Hobbies"].dropna()
    mssql.drop_database() # delete this line eventually?
    # save cities, regions and hobbies in mssql.
    mssql.create_city_table_sqldb(cities_regions)
    mssql.create_hobbies_table_sqldb(hobbies)
    return names_genders, surnames, cities_regions, hobbies


def create_data():
    names, surnames, cities_regions, hobbies = get_data()
    users_df = pd.DataFrame() # df that stores all users
    number_of_users = 500 # number of users to be created
    users_credentials_array = [] # array that stores email and pwd for users
    global USER_NUM # global variable that serves as an ID for users
    # each iteration creates a single user
    for user_num in range(number_of_users):
        try:
            date_of_birth, age = calculate_age(number_of_users, user_num) # calucalte age and date of birth for the user
            name_and_gender = names.sample(n=1) # sample returns a random item from an axis of object.
            name = name_and_gender['Name'].iloc[0]
            gender = name_and_gender['Gender'].iloc[0]
            surname = surnames.sample(n=1).iloc[0]
            city_and_region = cities_regions.sample(n=1)
            city =  city_and_region['Cities'].iloc[0]
            region =  city_and_region['Regions'].iloc[0]
            hobby = hobbies.sample(n=1).iloc[0]
            main.USER_NUM += 1
            cur_user = pd.DataFrame(
                {"user_num":[main.USER_NUM],"name": [name], "gender": [gender], "surname": [surname], "date_of_birth": [date_of_birth],
                 "age": [age], "city": [city], "region": [region], "hobby": [hobby]})
            #users = users.append(cur_user, ignore_index=True, sort=True)
            users_df = pd.concat([users_df, cur_user], ignore_index=True, sort=True)
            email_address = name + "." + surname + str(random.randint(0, 100)) + "@gmail.com"
            characters = string.ascii_letters + string.digits
            user_password = ''.join(random.choice(characters) for character in range(8))
            users_credentials_array.append((main.USER_NUM, email_address, user_password))
            # print(email_address+" "+user_password)
        except Exception as e:
            print("error")
            # print(e)
            print(e.message)
            continue
    pd.set_option('display.max_columns', None)
    #print(users_df)
    #print(cur_user.head())
    #mssql.save_in_sqldb(users_credentials_array)
    # print(len(users))
    #users_df.to_csv('data.csv', encoding='utf-8', index = False)
    return users_df

def calculate_age(number_of_users, user_num):
#this function recieves a year, and returns an age and date of birth.
    today = datetime.date.today() # get today's date
    flag = "Incorrect data format"
    while(flag == "Incorrect data format"):  # while the date is inccorect - keep looping. Stop when date is correct.
        try:
            if(user_num <= number_of_users*0.7): # make sure that 70% of the users are young
                date_of_birth = datetime.date(random.randint(1987, 2005), random.randint(1, 12), random.randint(1, 31))
            else:
                date_of_birth = datetime.date(random.randint(1952, 2008), random.randint(1, 12), random.randint(1, 31))
            flag = "Correct data format"
        except:
            flag == "Incorrect data format"
            continue
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day)) # calculate age
    return date_of_birth, age

