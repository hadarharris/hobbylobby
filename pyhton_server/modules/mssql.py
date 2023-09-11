from main import USER_NUM
import pyodbc #connection to MSSQL
database_name = "hobby_lobby_sql"

def drop_database():
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;'
        connection = pyodbc.connect(connection_string, autocommit = True)
        cursor = connection.cursor() 
        #create DB if does not exist
        #cnxn = pyodbc.connect(connection_string,autocommit = True)
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
                        Password nvarchar(8) NOT NULL
                        )"""

        cursor.execute(SQLCommand)

        SQLCommand = """INSERT INTO users(Usernum, Email, Password) VALUES"""
        for i in range(len(users_credentials)):
            user_num, email, pwd = users_credentials[i]
            if i == len(users_credentials)-1:
                SQLCommand += f"('{user_num}','{email}','{pwd}');"
            else:
                SQLCommand += f"('{user_num}','{email}','{pwd}'), "

        # print(SQLCommand)
        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()

        
    except Exception as e:
        print(e)

    """finally:
        if (connection.State == System.Data.ConnectionState.Open):
            connection.close()"""


def create_city_table_sqldb(cities_regions):
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database='+database_name+';Trusted_Connection=True;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        # SQLCommand = "USE "+database_name+";"
        
        #cursor.execute(SQLCommand)

        #SQL Query
        SQLCommand = """DROP TABLE IF EXISTS cities;
                        IF NOT EXISTS 
                                (
                                  SELECT name FROM sys.tables 
                                  WHERE name = 'cities'
                                )
                        CREATE TABLE cities
                        (
                        city nvarchar(50) NOT NULL,
                        region nvarchar(50) NOT NULL
                        )"""

        cursor.execute(SQLCommand)

        SQLCommand = """INSERT INTO cities(city, region) VALUES"""
        for i in range(len(cities_regions)):
            city_and_region = cities_regions.sample(n=1)
            city =  city_and_region['Cities'].iloc[0]
            region =  city_and_region['Regions'].iloc[0]
            if i == len(cities_regions)-1:
                SQLCommand += f"('{city}','{region}');"
            else:
                SQLCommand += f"('{city}','{region}'), "
        # print(SQLCommand)
        cursor.execute(SQLCommand)   
   
        #Commiting any pending transaction to the database.  
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(e)

    """finally:
        if (connection.State == System.Data.ConnectionState.Open):
            connection.close()"""


def create_hobbies_table_sqldb(hobbies):
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database='+database_name+';Trusted_Connection=True;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        #SQL Query
        SQLCommand = """DROP TABLE IF EXISTS hobbies;
                        IF NOT EXISTS 
                                (
                                  SELECT name FROM sys.tables 
                                  WHERE name = 'hobbies'
                                )
                        CREATE TABLE hobbies
                        (
                        hobby nvarchar(50) NOT NULL,
                        sub_category nvarchar(50) NOT NULL,
                        super_category nvarchar(50) NOT NULL
                        )"""

        cursor.execute(SQLCommand)

        SQLCommand = """INSERT INTO hobbies(hobby, sub_category, super_category) VALUES"""
        for i in range(len(hobbies)):
            hobby_and_category = hobbies.sample(n=1)
            hobby = hobby_and_category['Hobby'].iloc[0]
            category = hobby_and_category['Category'].iloc[0]
            sub_category = hobby_and_category['Sub_Category'].iloc[0]
            if i == len(hobbies)-1:
                SQLCommand += f"('{hobby}','{sub_category}','{category}');"
            else:
                SQLCommand += f"('{hobby}','{sub_category}','{category}'), "
        # print(SQLCommand)
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
    try: 
        #creating connection Object which will contain SQL Server Connection  
        connection_string = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database='+database_name+';Trusted_Connection=True;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor() 
        #SQL Query
        SQLCommand = query
        cursor.execute(SQLCommand)
        results = cursor.fetchall()
        if(results):
            return results
        else:
            print("data not found")
            return None
    except Exception as e:
        print(e)


def check_if_user_exists_sql(email,pwd):
    # check if user login credentials exist in mssml
    if(select_from_mssql(f"select * from users where Email='{email}' and Password='{pwd}'")):
        return True
    return False


def fetch_cities_sql():
    # fetch all cities and regions from mssml
    cities_query_res = select_from_mssql(f"select city, region from cities")
    cities = dict()
    for city_res in cities_query_res:
        city, region = city_res
        cities[city] = region
    return cities           


def fetch_hobbies_sql():
    # fetch all cities and regions from mssml
    hobbies_query_res = select_from_mssql(f"select hobby, sub_category, super_category from hobbies")
    hobbies = dict()
    for hobby_res in hobbies_query_res:
        hobby, sub_category, super_category = hobby_res
        hobbies[hobby] = {"sub_category": sub_category, "super_category": super_category}
    return hobbies 


if __name__ == "__main__":
    print(fetch_cities_sql())
    


