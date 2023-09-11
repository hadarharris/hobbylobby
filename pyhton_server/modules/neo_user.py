import main
from neo4j import GraphDatabase
from User import User
uri = "bolt://localhost:7687"
username = "neo4j"
password = "1234"

def addAll(elbow_point, users_df, cluster_centers):
    # Save the users and their clusters in Neo4j
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            session.execute_write(delete_nodes)
            # Create cluster nodes
            cluster_ids = []
            for cluster in range(elbow_point):
                cluster_id = session.execute_write(create_cluster_node)
                cluster_ids.append(cluster_id)

            # Create user nodes and relationships with their respective cluster node
            for user_index, user_row in users_df.iterrows():
                user_id = session.execute_write(create_user, user_row['user_num'], user_row['name'], user_row['surname'], user_row['gender'], user_row['date_of_birth'], str(user_row['age']), user_row['city'], user_row['region'], user_row['hobby'])
                cluster_id = cluster_ids[user_row['cluster']]
                session.execute_write(create_cluster_relation, cluster_id, user_id)

            # Create cluster relationship with its respective cluster center
            for cluster_index, cluster_center in enumerate(cluster_centers):
                cluster_id = cluster_ids[cluster_index]
                cluster_center_id = session.execute_write(create_cluster_center_node)
                session.execute_write(create_cluster_center_relation, cluster_id, cluster_center_id)
                
        driver.close()
        print("finished")
    except Exception as e:
        print("save_in_neo error ", e)


def create_user(tx, user_num, name,surname, gender, date_of_birth, age, city,region, hobby):
    user_details = """user_num: $user_num, name: $name, surname: $surname, gender: $gender, date_of_birth: $date_of_birth, age: $age, city: $city,
    region: $region, hobby: $hobby"""
    query_str = "CREATE (u:User {"+user_details+"}) return id(u)"
    user = tx.run(query_str, user_num=user_num, name=name, surname=surname, gender = gender, date_of_birth=date_of_birth, age=age, city=city,region=region, hobby=hobby)   
    return (user.values()[0])[0]


def create_cluster_relation(tx, cluster_id, user_id):
    """
    create relation to node representing a cluster
    """
    tx.run("""MATCH (u:User) WHERE id(u) = $user_id 
           MATCH (c:Cluster) WHERE id(c) = $cluster_id
           CREATE (u)-[:IN_CLUSTER]->(c)""",
           user_id=user_id, cluster_id=cluster_id)


def create_cluster_center_relation(tx, cluster_id, cluster_center_id):
    """
    create relation to node representing a cluster center
    """
    tx.run("""MATCH (c:Cluster) WHERE id(c) = $cluster_id
           MATCH (cc:ClusterCenter) WHERE id(cc) = $cluster_center_id
           CREATE (cc)-[:HAS_CENTER]->(c)""",
           cluster_id=cluster_id, cluster_center_id=cluster_center_id)


def delete_nodes(tx):
    tx.run("MATCH (n) DETACH DELETE n")


def create_cluster_node(tx):
    # create a node representing a cluster and returns the node's id created by neo
    cluster = tx.run("CREATE (c:Cluster) return id(c)")
    return (cluster.values()[0])[0]


def create_cluster_center_node(tx):
    # create a node representing a cluster center and returns the node's id created by neo
    cluster_center = tx.run("CREATE (cc:ClusterCenter) return id(cc)")
    return (cluster_center.values()[0])[0]

"""
match (c:Cluster)--(u:User)
where id(c) = 750
return c,u
"""

def save_in_neo(sub_cluster_users):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            session.execute_write(delete_nodes)
            # create cluster node
            x=0
            for k in range (len(sub_cluster_users)): 
                for j in range(len(sub_cluster_users[k])):
                    cluster_id = session.execute_write(create_cluster_node)
                    for i in range(len(sub_cluster_users[k][j])):
                        user_id = session.execute_write(create_user, sub_cluster_users[k][j][i]["user_num"],
                                                sub_cluster_users[k][j][i]["name"], sub_cluster_users[k][j][i]["surname"],
                                                sub_cluster_users[k][j][i]["gender"],
                                                sub_cluster_users[k][j][i]["date_of_birth"],str(sub_cluster_users[k][j][i]["age"]),
                                                sub_cluster_users[k][j][i]["city"],sub_cluster_users[k][j][i]["region"],
                                                sub_cluster_users[k][j][i]["hobby1"],sub_cluster_users[k][j][i]["hobby2"],sub_cluster_users[k][j][i]["hobby3"],
                                                sub_cluster_users[k][j][i]["category1"],sub_cluster_users[k][j][i]["category2"],
                                                sub_cluster_users[k][j][i]["category3"],sub_cluster_users[k][j][i]["sub_category1"],
                                                sub_cluster_users[k][j][i]["sub_category2"],sub_cluster_users[k][j][i]["sub_category3"])
                        session.execute_write(create_cluster_relation,cluster_id, user_id)
                        x=x+1
                        #print(user_id)
        driver.close()
        print(x)
    except Exception as e:
        print("save_in_neo error ",e)
        return None



def save_new_user_in_neo(name,surname,gender,dob,city,hobby1,hobby2,hobby3):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        #global USER_NUM
        main.USER_NUM+=1
        with driver.session() as session: 
            added_user_id = session.execute_write(create_user, main.USER_NUM, name,surname, gender, dob, "25", city,"a", 
               hobby1, hobby2, hobby3, "", "", "", 
               "", "", "")
            print(added_user_id)
        driver.close()
        return added_user_id
    except Exception as e:
        print("save_new_user_in_neo error ",e)
        return None

"""
    def fetch_data_from_neo(tx, query):
        data = tx.run(query)
        return (data.values())
"""

def get_all():
    try:
        # function to fetch one user from neo
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        ###
        with driver.session() as session:
            query = "match (n:User) return n"
            users = session.run(query)
            result = [record for record in users.data()]
            user_lst = []
            for i in range(len(result)):
                u = User(result[i]['n'].get('name'),result[i]['n'].get('gender'),result[i]['n'].get('surname'),result[i]['n'].get('date_of_birth'),
                     result[i]['n'].get('city'),result[i]['n'].get('region'),result[i]['n'].get('hobby1'),result[i]['n'].get('hobby2'),
                     result[i]['n'].get('hobby3'),result[i]['n'].get('category1'),result[i]['n'].get('category2'),result[i]['n'].get('category3'),
                     result[i]['n'].get('sub_category1'),result[i]['n'].get('sub_category2'),result[i]['n'].get('sub_category3'))
                user_lst.append(u.__dict__)
        driver.close()
        return user_lst
    except Exception as e:
        print("get_all error ",e)
        return None



### change returned field 
def get_user_from_neo(user_id_to_fetch):
    try:
        # function to fetch one user from neo
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        ###
        with driver.session() as session:
            query = "match (n:User{user_num:"+str(user_id_to_fetch)+"}) return n"
            user = session.run(query)
            result = [record for record in user.data()]
            """
            for i in range(len(results)):
               u = User(results[i]['n'].get('name'),results[i]['n'].get('gender'),results[i]['n'].get('surname'))
               print(u)
            """
            u = User(result[0]['n'].get('name'),result[0]['n'].get('gender'),result[0]['n'].get('surname'),result[0]['n'].get('date_of_birth'),
                     result[0]['n'].get('city'),result[0]['n'].get('region'),result[0]['n'].get('hobby1'),result[0]['n'].get('hobby2'),
                     result[0]['n'].get('hobby3'),result[0]['n'].get('category1'),result[0]['n'].get('category2'),result[0]['n'].get('category3'),
                     result[0]['n'].get('sub_category1'),result[0]['n'].get('sub_category2'),result[0]['n'].get('sub_category3'))
            # print(u)
        driver.close()
        return u.__dict__
    except Exception as e:
        print("get_user_from_neo error ",e)
        return None


def get_cluster_users_from_neo(user_num):
    try:
        # function to fetch several users by clusters from neo
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            query = "match (u:User{user_num:"+str(user_num)+"})--(c:Cluster)--(n:User) return n "
            users = session.run(query)
            results = [record for record in users.data()]
            user_lst = []
            for i in range(len(results)):
                u = User(result[i]['n'].get('name'),result[i]['n'].get('gender'),result[i]['n'].get('surname'),result[i]['n'].get('date_of_birth'),
                     result[i]['n'].get('city'),result[i]['n'].get('region'),result[i]['n'].get('hobby1'),result[i]['n'].get('hobby2'),
                     result[i]['n'].get('hobby3'),result[i]['n'].get('category1'),result[i]['n'].get('category2'),result[i]['n'].get('category3'),
                     result[i]['n'].get('sub_category1'),result[i]['n'].get('sub_category2'),result[i]['n'].get('sub_category3'))
                user_lst.append(u.__dict__)
        driver.close()
        return user_lst
    except Exception as e:
        print("get_cluster_users_from_neo error ",e)
        return None

def update_user(body):
    try:
        # function to fetch several users by clusters from neo
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            '''query = "match (u:User{user_num:"+body.user_num+"}) set u.name= "+ body.name +", u.surname= "+ body.surname +", u.gender= "+ body.gender+", u.city= "+ body.city
                +", u.region= "+ body.region +", u.hobby1= "+ body.hobby1+", u.hobby2= "+ body.hobby2+", u.hobby3= "+ body.hobby3+", u.category1= "+ body.category1 +", u.category2= "+body.category2 
                +", u.category3= "+body.category3+", u.sub_category1= "+body.sub_category1+", u.sub_category2= "+body.sub_category2+", u.sub_category3= "+body.sub_category3'''
            
            query = "match (u:User{user_num:"+body["user_num"]+"}) set u.name= '"+ body["name"] +"', u.surname= '"+ body["surname"] + "', u.gender= '"+ body["gender"] \
            +"', u.city= '"+ body["city"] +"', u.region= '"+ body["region"] +"', u.hobby1= '"+ body["hobby1"]+"', u.hobby2= '"+ body["hobby2"] \
            +"', u.hobby3= '"+ body["hobby3"]+"', u.category1= '"+ body["category1"] +"', u.category2= '"+body["category2"] +"', u.category3= '"+body["category3"] \
            +"', u.sub_category1= '"+body["sub_category1"]+"', u.sub_category2= '"+body["sub_category2"]+"', u.sub_category3= '"+body["sub_category3"]+"'"
            print(query)
            users = session.run(query)   
            
        driver.close()
    except Exception as e:
        print("update_user error ",e)
        return None


if __name__ == "__main__":
    bodydict = {"user_num":"1","name":"alex","surname":"cohen","gender":"male","city":"london","region":"london","hobby1":"x","hobby2":"y","hobby3":"z","category1":"a","category2":"b","category3":"c"
                 ,"sub_category1":"l","sub_category2":"m","sub_category3":"n"}
    update_user(bodydict)