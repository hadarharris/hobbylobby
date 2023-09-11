import pyodbc #connection to MSSQL
database_name = "hobby_lobby_sql"

def create_hobby_lobby_database():
    # Function to create the 'hobby_lobby_sql' database
    try:
        # Connect to the SQL Server master database
        connection = pyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;Encrypt=False', autocommit=True)
        cursor = connection.cursor()

        # SQL script to check and create the database
        create_db_script = """
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'hobby_lobby_sql')
        BEGIN
            CREATE DATABASE hobby_lobby_sql;
        END
        """
        
        # Execute the SQL script
        cursor.execute(create_db_script)
        print("Database 'hobby_lobby_sql' created successfully.")
        
    except Exception as e:
        print("Error creating database:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def drop_database():
    # Function to drop the 'hobby_lobby_sql' database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;Encrypt=False'
        connection = pyodbc.connect(connection_string, autocommit = True)
        cursor = connection.cursor() 
        #create DB if does not exist
        cursor.execute('''
        USE master
        IF NOT EXISTS (
            SELECT name
                FROM sys.databases
                WHERE name = N'{}')
        CREATE DATABASE {} '''.format(database_name,database_name))
        cursor.close()
    except Exception as e:
        print(e)


def save_in_sqldb(users_credentials):
    # Function to save user credentials in the SQL database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        SQLCommand = "USE "+database_name+";"
        
        cursor.execute(SQLCommand)

        #SQL Query
        SQLCommand = """DROP TABLE IF EXISTS users;
                        IF NOT EXISTS 
                                (
                                  SELECT name FROM sys.tables 
                                  WHERE name = 'users'
                                )
                        CREATE TABLE users
                        (
                        Usernum nvarchar(10) PRIMARY KEY,
                        Email nvarchar(50) NOT NULL,
                        Password nvarchar(14) NOT NULL
                        )"""

        cursor.execute(SQLCommand)

        SQLCommand = """INSERT INTO users(Usernum, Email, Password) VALUES"""
        for i in range(len(users_credentials)):
            user_num, email, pwd = users_credentials[i]
            if i == len(users_credentials)-1:
                SQLCommand += f"('{user_num}','{email}','{pwd}');"
            else:
                SQLCommand += f"('{user_num}','{email}','{pwd}'), "
        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()

        return True
        
    except Exception as e:
        print(e)
        return False


def create_city_table_sqldb(cities):
    # Function to create a 'cities' table and insert city names into the SQL database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database='+database_name+';Trusted_Connection=True;Encrypt=False'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 

        #SQL Query
        SQLCommand = """DROP TABLE IF EXISTS cities;
                        IF NOT EXISTS 
                                (
                                  SELECT name FROM sys.tables 
                                  WHERE name = 'cities'
                                )
                        CREATE TABLE cities
                        (
                        city nvarchar(50) NOT NULL
                        )"""

        cursor.execute(SQLCommand)

        SQLCommand = """INSERT INTO cities(city) VALUES"""
        for i in range(len(cities)):
            city =  cities[i]
            if i == len(cities)-1:
                SQLCommand += f"('{city}');"
            else:
                SQLCommand += f"('{city}'), "
        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(e)

    """finally:
        if (connection.State == System.Data.ConnectionState.Open):
            connection.close()"""

def select_from_mssql(query):
    # Function to execute a SELECT query on the SQL database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database='+database_name+';Trusted_Connection=True;Encrypt=False'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        #SQL Query
        SQLCommand = query
        cursor.execute(SQLCommand)
        results = cursor.fetchall()
        if(results):
            return results
        else:
            return None
    except Exception as e:
        print(e)


def check_if_user_exists_sql(email,pwd):
    # Function to check if a user with the given email and password exists in the SQL database
    if(select_from_mssql(f"select * from users where Email='{email}' and Password='{pwd}'")):
        return True
    return False

def check_if_email_exists_sql(email):
    # Function to check if a user with the given email exists in the SQL database
    if(select_from_mssql(f"select * from users where Email='{email}'")):
        return True
    return False

def check_if_other_user_exists_sql(email,usernum):
    # Function to check if another user with the given email exists in the SQL database (used for updating user information)
    if(select_from_mssql(f"select * from users where Email='{email}' and Usernum<>'{usernum}'")):
        return True
    return False

def fetch_cities_sql():
    # Function to fetch all city names from the SQL database
    cities_query_res = select_from_mssql(f"select city from cities")
    cities = list([row[0] for row in cities_query_res])
    return cities           

def fetch_users_sql():
    # Function to fetch all user data from the SQL database
    users_query_res = select_from_mssql(f"select Usernum, Email, Password from users")
    users = dict()
    for user_res in users_query_res:
        usernum, email, password = user_res
        users[ usernum] = {"password": password, "email": email}
    return users

def fetch_user_sql(usernum):
    # Function to fetch a specific user's data from the SQL database based on user number
    user_query_res = select_from_mssql(f"SELECT Usernum, Email, Password FROM users WHERE Usernum = {usernum}")
    user = None  # Initialize the user as None
    for user_res in user_query_res:
        usernum, email, password = user_res
        user = {"usernum": usernum, "password": password, "email": email}
        break  # Exit the loop after the first user is found
    return user

def save_new_user_sqldb(user_num, email, pwd):
    # Function to save a new user in the SQL database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;Encrypt=False'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        SQLCommand = "USE "+database_name+";"
        
        cursor.execute(SQLCommand)

        SQLCommand = "INSERT INTO users(Usernum, Email, Password) VALUES " f"('{user_num}','{email}','{pwd}');"

        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()

        return True
        
    except Exception as e:
        print(e)
        return False


def update_user_sqldb(user_num, email, pwd):
    # Function to update a user's data in the SQL database
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;Encrypt=False'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        SQLCommand = "USE "+database_name+";"
        
        cursor.execute(SQLCommand)

        SQLCommand = f"UPDATE users SET Email='{email}', Password='{pwd}' WHERE Usernum='{user_num}';"

        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()

        return True
        
    except Exception as e:
        print(e)
        return False
    
