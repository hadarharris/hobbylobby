from asyncio.windows_events import NULL
from pickle import NONE
import kmeans
import main
import create_data
from neo4j import GraphDatabase
import pandas as pd

uri = "neo4j+s://99bb5952.databases.neo4j.io"
username = "neo4j"
password = "12345678"

def addAll(elbow_point, users_df, cluster_centers):
    # Save the users and their clusters in Neo4j
    try:
        print("Adding all")
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print("Adding all")
        with driver.session() as session:
            session.execute_write(delete_nodes)
            # Create cluster nodes and set their respective cluster centers as properties
            cluster_ids = []
            for i, centroid in enumerate(cluster_centers):
                cluster_center = centroid
                cluster_id = session.execute_write(lambda tx: create_cluster_node(tx, cluster_center))
                cluster_ids.append(cluster_id)

            # Create user nodes and relationships with their respective cluster node
            for user_index, user_row in users_df.iterrows():
                print("adding user ",user_row['user_num'])
                user_id = session.execute_write(
                    lambda tx: create_user(tx, user_row['user_num'], user_row['name'], user_row['surname'],
                                           user_row['gender'], user_row['date_of_birth'],
                                           user_row['city'], user_row['hobby'], user_row['cluster']))
                cluster_id = cluster_ids[user_row['cluster']]
                session.execute_write(lambda tx: create_cluster_relation(tx, cluster_id, user_id))

        driver.close()
        print("Finished adding all")
    except Exception as e:
        print("Error while saving all users in Neo4j", e)


def delete_nodes(tx):
    tx.run("MATCH (n) DETACH DELETE n")


def create_cluster_node(tx, cluster_center):
    query_str = "CREATE (c:Cluster {centroid: $centroid}) RETURN id(c)"
    cluster = tx.run(query_str, centroid=cluster_center)
    return cluster.single()[0]


def create_user(tx, user_num, name, surname, gender, date_of_birth, city, hobby, cluster):
    query_str = "CREATE (u:User {user_num: $user_num, name: $name, surname: $surname, gender: $gender, date_of_birth: $date_of_birth, city: $city, hobby: $hobby, cluster: $cluster}) RETURN id(u)"
    user = tx.run(query_str, user_num=user_num, name=name, surname=surname, gender=gender,
                  date_of_birth=date_of_birth, city=city, hobby=hobby, cluster=cluster)
    return user.single()[0]


def create_cluster_relation(tx, cluster_id, user_id):
    query_str = "MATCH (u:User), (c:Cluster) WHERE id(u)=$user_id AND id(c)=$cluster_id CREATE (u)-[:BELONGS_TO]->(c)"
    tx.run(query_str, user_id=user_id, cluster_id=cluster_id)

def add_user(user_data):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            session.write_transaction(create_user, user_data)
        driver.close()
        print("User added successfully")
    except Exception as e:
        print("Error while adding user to Neo4j:", e)

def update_user_neo(user_data):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            # Check if the hobby value is different before updating
            current_hobby = get_user_hobby(session, user_data["user_num"])
            session.write_transaction(_update_user, user_data)
            if current_hobby != user_data["hobby"]:
                print("Hobby value is differnt")
                kmeans.kmeansclustering()
            else:
                print("Hobby value is the same.")
        driver.close()
        return True
    except Exception as e:
        print("Error while updating user in Neo4j:", e)
        return False

def get_user_hobby(tx, user_num):
    query_str = "MATCH (u:User {user_num: $user_num}) RETURN u.hobby AS hobby"
    result = tx.run(query_str, user_num=user_num).single()
    if result:
        return result["hobby"]
    else:
        return None

def _update_user(tx, user_data):
    query_str = """
    MATCH (u:User {user_num: $user_num})
    SET u.name = $name,
        u.surname = $surname,
        u.gender = $gender,
        u.city = $city,
        u.dob = $dob,
        u.hobby = $hobby
    """
    tx.run(query_str, user_num=user_data["user_num"], name=user_data["name"], surname=user_data["surname"],
           gender=user_data["gender"], city=user_data["city"], dob=user_data["date_of_birth"], hobby=user_data["hobby"])

def get_all_clusters():
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.read_transaction(fetch_all_clusters)
        driver.close()
        return result
    except Exception as e:
        print("Error while retrieving clusters from Neo4j:", e)


def fetch_all_clusters(tx):
    query_str = "MATCH (c:Cluster) RETURN c"
    result = tx.run(query_str)
    clusters = [record['c'] for record in result]
    return clusters

def get_all_users_df():
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            users = session.read_transaction(fetch_all_users)
        driver.close()
        
        # Convert the list of user dictionaries to a DataFrame
        users_df = create_data.pd.DataFrame(users)
        return users_df
    except Exception as e:
        print("Error while retrieving users from Neo4j:", e)
        return None

def fetch_all_users(tx):
    query_str = "MATCH (u:User) RETURN u"
    result = tx.run(query_str)
    users = [record['u'] for record in result]
    return users

def is_database_empty():
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.read_transaction(check_empty)
        driver.close()
        return result
    except Exception as e:
        print("Error while checking database status:", e)
        return True  # Assume the database is empty in case of an error

def check_empty(tx):
    query_str = "MATCH (u:User) RETURN COUNT(u) AS user_count"
    user_count = tx.run(query_str).single()["user_count"]

    query_str = "MATCH (c:Cluster) RETURN COUNT(c) AS cluster_count"
    cluster_count = tx.run(query_str).single()["cluster_count"]

    return user_count == 0 and cluster_count == 0

def create_new_user(tx, user_data):
    query_str = """
    CREATE (u:User {user_num: $user_num, name: $name, surname: $surname, gender: $gender, 
    date_of_birth: $dob, city: $city, hobby: $hobbies})
    RETURN id(u)
    """
    user = tx.run(query_str, user_num=user_data['user_num'], name=user_data['name'], surname=user_data['surname'],
                  gender=user_data['gender'], dob=user_data['dob'],
                  city=user_data['city'], hobbies=user_data['hobbies'])
    return user.single()[0]

def add_user_to_neo4j(user_data):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        
        with driver.session() as session:
            user_num = generate_unique_user_num(session)
            user_data["user_num"] = user_num
            
            session.write_transaction(create_new_user, user_data)
        return user_num
            
        driver.close()
        print("User added successfully")
    except Exception as e:
        print("Error while adding user to Neo4j:", e)
        return user_num  

def generate_unique_user_num(session):
    while True:
        random_num = create_data.random.randint(501, 9999)  # Adjust the range as needed
        if is_user_num_unique(session, random_num):
            return random_num

def is_user_num_unique(session, user_num):
    query = "MATCH (u:User {user_num: $user_num}) RETURN COUNT(u) AS count"
    result = session.run(query, user_num=user_num)
    count = result.single()["count"]
    return count == 0

def get_user_details_from_neo(user_num):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        
        with driver.session() as session:
            user_details = session.read_transaction(fetch_user_details, user_num)
            print("user_details", user_details)
        driver.close()
        return user_details
    except Exception as e:
        print("Error while retrieving user details from Neo4j:", e)
        return None

def fetch_user_details(tx, user_num):
    query_str = "MATCH (u:User) WHERE u.user_num = $user_num RETURN u"
    result = tx.run(query_str, user_num=user_num)
    for record in result:
        return record
    else:
        return None  

def get_cluster_users(user_num):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        
        with driver.session() as session:
            user_details = session.read_transaction(fetch_cluster, user_num)
        driver.close()
        return user_details
    except Exception as e:
        print("Error while retrieving user details from Neo4j:", e)
        return None  

def fetch_cluster(tx, user_num):
    query_str = "MATCH (n:User{user_num:$user_num})--(c:Cluster)--(m:User) RETURN m"
    result = tx.run(query_str, user_num=user_num)
    users=list()
    for record in result:
        users.append(record)
    return users

def get_all_other_users(user_num):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        
        with driver.session() as session:
            user_details = session.read_transaction(fetch_all_but_me, user_num)
        driver.close()
        return user_details
    except Exception as e:
        print("Error while retrieving user details from Neo4j:", e)
        return None  

def fetch_all_but_me(tx, user_num):
    query_str = (
    "MATCH (user:User)-[:BELONGS_TO]->(cluster:Cluster) " +  # Assuming a relationship name of BELONGS_TO
    "WHERE user.user_num = $user_num " +
    "WITH cluster " +
    "MATCH (otherUser:User)-[:BELONGS_TO]->(cluster) " +
    "WHERE otherUser.user_num <> $user_num " +
    "RETURN otherUser"
    )
    result = tx.run(query_str, user_num=user_num)
    users=list()
    for record in result:
        users.append(record)
    return users


def get_users_with_hobby(user_num, search_string, search_method):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()

        with driver.session() as session:
            user_details = session.read_transaction(fetch_users_by_hobby, user_num, search_string, search_method)
        driver.close()
        return user_details
    except Exception as e:
        print("Error while retrieving user details from Neo4j:", e)
        return None


def fetch_users_by_hobby(tx, user_num, search_string, search_method):
    fixed_string = kmeans.process_data(pd.DataFrame({'hobby': [search_string]}))[0][0]
    words = fixed_string.split()  # Split the search string into words

    if search_method == 'exact':
        query_str = (
            "MATCH (n:User) WHERE n.user_num <> $user_num AND "
            "all(word IN $words WHERE toLower(n.hobby) CONTAINS toLower(word)) "
            "RETURN n"
        )
        result = tx.run(query_str, user_num=user_num, words=words)
    elif search_method == 'or':
        query_str = (
            "MATCH (n:User) WHERE n.user_num <> $user_num AND "
            "any(word IN $words WHERE toLower(n.hobby) CONTAINS toLower(word)) "
            "RETURN n"
        )
        result = tx.run(query_str, user_num=user_num, words=words)

    users = [record["n"] for record in result]
    return users

def add_friend(user_num, friend_num):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()

        with driver.session() as session:
            users_details = session.write_transaction(add_friendship, user_num, friend_num)
        driver.close()
        return users_details
    except Exception as e:
        print("Error while adding friend to Neo4j:", e)
        return None


def add_friendship(tx, user_num, friend_num):
    query_str = (
            "MATCH (u:User), (f:User) "
            "WHERE u.user_num =$user_num AND f.user_num=$friend_num "
            "CREATE (u)-[:FRIEND]->(f) "
            "RETURN u, f"
        )    
    result = tx.run(query_str, user_num=user_num, friend_num=friend_num)
    return result

def remove_friend(user_num, friend_num):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()

        with driver.session() as session:
            users_details = session.write_transaction(remove_friendship, user_num, friend_num)
        driver.close()
        return users_details
    except Exception as e:
        print("Error while removing friend from Neo4j:", e)
        return None


def remove_friendship(tx, user_num, friend_num):
    query_str = (
            "MATCH (u:User)-[r:FRIEND]->(f:User) "
            "WHERE u.user_num =$user_num AND f.user_num=$friend_num "
            "DELETE r "
            "return u, f"
        )    
    result = tx.run(query_str, user_num=user_num, friend_num=friend_num)
    return result 

def check_friend(user_num, friend_num):
    #this funtion returns true if user with user_num added user with friend_num as a friend, and returns else otherwise
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()

        with driver.session() as session:
            is_friend = session.read_transaction(check_friendship, user_num, friend_num)
        driver.close()
        return is_friend 
    except Exception as e:
        print("Error while checking if friendship exists in Neo4j:", e)
        return None


def check_friendship(tx, user_num, friend_num):
    query_str = (
            "MATCH (u:User), (f:User) "
            "WHERE u.user_num =$user_num AND f.user_num=$friend_num "
            "RETURN EXISTS((u)-[:FRIEND]->(f))"
        )    
    result = tx.run(query_str, user_num=user_num, friend_num=friend_num)
    return result.single()[0]

def get_all_friends(user_num):
    #this funtion returns true if user with user_num added user with friend_num as a friend, and returns else otherwise
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()

        with driver.session() as session:
            users_details = session.read_transaction(get_friends_from_neo, user_num)
        driver.close()
        return users_details 
    except Exception as e:
        print("Error while checking if friendship exists in Neo4j:", e)
        return None


def get_friends_from_neo(tx, user_num):
    query_str = (
            "MATCH (u:User)-[:FRIEND]->(f:User) "
            "WHERE u.user_num =$user_num "
            "RETURN f"
        )    
    result = tx.run(query_str, user_num=user_num)
    users=list()
    for record in result:
        users.append(record)
    return users  

#updating users when rerunning kmeans
def updateAll(users_df, cluster_centers):
    # Save the users and their clusters in Neo4j
    try:
        print("updating all")
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            session.execute_write(delete_cluster_nodes)
            # Create cluster nodes and set their respective cluster centers as properties
            cluster_ids = []
            for i, centroid in enumerate(cluster_centers):
                cluster_center = centroid
                cluster_id = session.execute_write(lambda tx: create_cluster_node(tx, cluster_center))
                cluster_ids.append(cluster_id)

            # Create user nodes and relationships with their respective cluster node
            for user_index, user_row in users_df.iterrows():
                print("updating user ",user_row['user_num'])
                user_id = session.execute_write(
                    lambda tx: _update_user(tx, user_row))
                cluster_id = cluster_ids[user_row['cluster']]
                session.execute_write(lambda tx: recreate_relations(tx, cluster_id, user_row['user_num']))

        driver.close()
        print("Finished updating all")
    except Exception as e:
        print("Error while saving all users in Neo4j", e)


def delete_cluster_nodes(tx):
    tx.run("MATCH (n:Cluster) DETACH DELETE n")

def recreate_relations(tx, cluster_id, user_num):
    query_str = "MATCH (u:User), (c:Cluster) WHERE u.user_num=$user_num AND id(c)=$cluster_id CREATE (u)-[:BELONGS_TO]->(c)"
    tx.run(query_str, user_num=user_num, cluster_id=cluster_id)
    
