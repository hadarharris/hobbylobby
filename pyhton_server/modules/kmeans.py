from main import neo_user
# This imports the KMeans clustering algorithm from the scikit-learn library,
# which is used for machine learning tasks such as clustering, classification, and regression.
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import create_data
# This imports the TfidfVectorizer class from scikit-learn,
# which is used for converting text data into a matrix of TF-IDF features.
from sklearn.feature_extraction.text import TfidfVectorizer
# This imports the cosine_similarity function from scikit-learn,
# which is used to calculate the cosine similarity between two vectors.
from sklearn.metrics.pairwise import cosine_similarity
# This imports the Natural Language Toolkit (nltk) library,
# which is used for natural language processing tasks such as tokenization, stemming, and lemmatization.
# The second line downloads the 'punkt' resource, which is used for tokenization.
import nltk
nltk.download('punkt')
# This imports the stopwords corpus from nltk,
# which is a collection of words that are commonly used in a language but do not carry much meaning in text analysis.
from nltk.corpus import stopwords
# This imports the word_tokenize function from nltk,
# which is used for tokenizing text into individual words.
from nltk.tokenize import word_tokenize
# This imports the WordNetLemmatizer class from nltk,
# which is used for lemmatizing words (reducing them to their base form).
from nltk.stem import WordNetLemmatizer
# This imports the LatentDirichletAllocation class from scikit-learn,
# which is used for topic modeling tasks.
# It is a generative probabilistic model that assumes each document consists of a mixture of topics.
from sklearn.decomposition import LatentDirichletAllocation
# The re module provides a variety of functions and methods for working with regular expressions.
import re
#  This downloads the stopwords corpus from NLTK,
# which contains a collection of words that are commonly used but typically don't contribute much meaning to a text.
nltk.download('stopwords')
# This downloads the WordNet corpus from NLTK,
# which is a lexical database of English that provides semantic relationships between words.
# This will be used later for lemmatization.
nltk.download('wordnet')


'''
dictionary:
{key-supercluster : val-sub dictionary{key-sub cluster, val-}}
'''

"""def predict_kmodes(data): # not in use in the meanwhile
    users_df = data
    kmode = KModes(n_clusters=3, init="random", verbose=1)
    clusters = kmode.fit_predict(users_df)
    print(clusters)"""

def predict_data():
     # Create a TF-IDF vectorizer.
    # This creates a TF-IDF vectorizer,
    # which is used to convert the raw text data into a numerical representation that can be used for clustering.
    tfidf_vectorizer = TfidfVectorizer()

    # This initializes a set of stop words using the stopwords corpus from NLTK to be removed from the text.
    stop_words = set(stopwords.words('english'))

    # This defines a list of custom stop words that are added to the existing set of stop words.
    custom_stop_words = ['enjoy', 'enjoyed', 'enjoying', 'enjoys', 'love', 'loved', 'loves', 'loving', 'hate',
                         'hated', 'hates', 'hating', 'like', 'liked', 'likes', 'liking', 'often', 'rarely']
    stop_words.update(custom_stop_words)

    # Define the words that are not considered stop words
    whitelist = ['not', 'very', 'no', 'nor', 'only', 'but', 'can']

    # Remove the whitelisted words from the stop words using a List Comprehension.
    # it's a short for statement with a conditional test
    stop_words = [word for word in stop_words if word not in whitelist]

    # Define the lemmatizer object, which will be used later to lemmatize the words in the text data.
    # it involves removing the inflectional endings of words and converting them into a common base or root form.
    # This process helps to reduce the number of unique words in the text data,
    # and can also improve the accuracy of analysis by grouping together words with similar meanings.
    # For example, the words "am", "are", "is" can all be lemmatized to "be",
    # and the words "walk", "walking", "walked" can all be lemmatized to "walk".
    lemmatizer = WordNetLemmatizer()

    #users_df = create_data.pd.read_csv("data.csv", low_memory=False)
    km_scores = {}
    users_df = create_data.create_data()

    # Preprocess the user data

    processed_data = [] # an empty list to store the processed data
    # This line iterates through each row of the users_df DataFrame.
    # index representing the index of the row
    for index, row in users_df.iterrows(): # Extract the user's hobbies and preprocess the text
        # modify the split() method to use regular expressions to split the string by any whitespace characters,
        # including multiple spaces.
        # because of a warning, we added r before the escape character to mark it as literal.
        hobbies = re.split(r'\s+', row['hobby'])
        hobbies = [h.strip().lower() for h in hobbies]
        hobbies = ' '.join(hobbies)
        hobbies = word_tokenize(hobbies)
        hobbies = [lemmatizer.lemmatize(word) for word in hobbies if word not in stop_words]
        hobbies = ' '.join(hobbies)
        # Combine the user's name, age, address, and preprocessed hobbies into a single string
        text = f"{row['name']} {row['gender']} {row['city']} {hobbies}"
        # Append the preprocessed text to the processed data
        processed_data.append(text)

    # Compute the TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_data)

    # Use Latent Dirichlet Allocation (LDA) to identify the most relevant topics in the text
    n_topics = 10
    lda = LatentDirichletAllocation(n_components=n_topics, max_iter=50,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(tfidf_matrix)

    # Generate candidate keywords by selecting the top words from each topic
    keywords = []
    for topic_idx, topic in enumerate(lda.components_):
        top_keywords_idx = topic.argsort()[::-1][:10]
        top_keywords = [tfidf_vectorizer.get_feature_names_out()[i] for i in top_keywords_idx]
        keywords.extend(top_keywords)

    # Remove duplicate keywords
    keywords = list(set(keywords))

    # Create a filter for the keywords
    keyword_filter = '|'.join(keywords)

    # Filter the hobbies based on the keywords
    users_df['filtered_hobbies'] = users_df['hobby'].str.lower().str.findall(keyword_filter).apply(
        lambda x: ', '.join(x))

    n_clusters_range = range(6,20)
    wcss = []
    for n_clusters in n_clusters_range:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        kmeans.fit(tfidf_matrix)
        wcss.append(kmeans.inertia_)

    # Plot the within-cluster sum of squares (WCSS) against the number of clusters
    #plt.plot(n_clusters_range, wcss)
    #plt.title('Elbow Method')
    #plt.xlabel('Number of clusters')
    #plt.ylabel('WCSS')
    #plt.show()

    # Determine the elbow point, which is the point of maximum curvature in the WCSS curve
    wcss_diff = create_data.np.diff(wcss)
    curvature = create_data.np.diff(wcss_diff)
    elbow_point = n_clusters_range[create_data.np.argmax(curvature)+1]

    # Cluster the users based on their filtered hobbies using the optimal number of clusters
    kmeans = KMeans(n_clusters=elbow_point, random_state=0)
    kmeans.fit_transform(tfidf_matrix)

    # Assign each user to a cluster based on the cosine similarity between their TF-IDF vector and the cluster centers
    users_df['cluster'] = kmeans.predict(tfidf_matrix)
    cluster_centers = kmeans.cluster_centers_
    # Compute the cosine similarity between each user's TF-IDF vector and the cluster centers
    similarity_matrix = cosine_similarity(tfidf_matrix, cluster_centers)

    # Find the index of the cluster center that has the highest similarity for each user
    cluster_indices = create_data.np.argmax(similarity_matrix, axis=1)

    # Assign the cluster label to each user based on the index of the most similar cluster center
    users_df['cluster'] = cluster_indices
    neo_user.addAll(elbow_point, users_df, cluster_centers)

    ## Print the users in each cluster
    #for cluster in range(n_clusters):
    #    if cluster >= elbow_point and len(users_df[users_df['cluster'] == cluster]) == 0:
    #        break  # Stop printing clusters after the elbow point with no people in them
    #    cluster_users = users_df[users_df['cluster'] == cluster]
    #    print(f"Cluster {cluster}:")
    #    for index, row in cluster_users.iterrows():
    #        print(f"- {row['name']}, {row['gender']}, {row['city']}: {row['hobby']}")
    #    print("\n")

    ##from py2neo import Graph, Node, Relationship

    ### Connect to the Neo4j database
    ##graph = Graph("bolt://localhost:7687", auth=("neo4j", "1234"))

    ### Create a constraint on the user name property to ensure uniqueness
    ##graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.name IS UNIQUE")

    ### Create the cluster nodes
    ##cluster_nodes = []
    ##for i in range(n_clusters):
    ##    cluster_node = Node("Cluster", name=f"Cluster{i}")
    ##    graph.create(cluster_node)
    ##    cluster_nodes.append(cluster_node)

    ### Create the user nodes and relationships to their corresponding clusters
    ##for index, row in users_df.iterrows():
    ##    user_node = Node("User", name=row['name'], gender=row['gender'], city=row['city'], hobby=row['hobby'])
    ##    graph.create(user_node)
    ##    cluster_node = cluster_nodes[row['cluster']]
    ##    relationship = Relationship(user_node, "BELONGS_TO", cluster_node)
    ##    graph.create(relationship)
    #max_score = 0
    #max_clusters = 0
    #max_pred = []
    ##new_users_df = users_df[["categoryID1", "categoryID2", "categoryID3"]]
    ##new_users_df = (create_data.pd.get_dummies(new_users_df, columns=['category1', 'category2', 'category3'], prefix_sep='super_', prefix=''))
    #new_users_df = new_users_df.groupby(level=0, axis=1).sum()
    #create_data.pd.set_option('display.max_columns', None)
    #for i in range(15, 25):
    #   clusterer = KMeans(n_clusters=i, n_init=10).fit(new_users_df[:200])
    #   #print(clusterer.cluster_centers_)
    #   cur_pred = clusterer.predict(new_users_df)
    #   cur_score = silhouette_score(new_users_df, cur_pred, metric='euclidean')
    #   if cur_score > max_score:
    #      max_score = cur_score
    #      max_clusters = i
    #      max_pred = cur_pred
    # return max_pred, users_df, max_clusters
    """
    clusterer = KMeans(n_clusters=25, n_init=10).fit(new_users_df[:100])
    cur_pred = clusterer.predict(new_users_df)
    return cur_pred, users_df, 25
    """
    # pd.set_option('display.max_columns', None)


def create_clusters():
    pred, users_df, n = predict_data()
    # print(type(users_df.loc[0]))
    clusters_arr = [[] for i in range(n)]
    #print("create clusters:", len(pred))
    for i in range(0, len(pred)):
        clusters_arr[pred[i]].append(users_df.loc[i])
    print(clusters_arr)
    return clusters_arr


def create_sub_clusters():
    clusters_arr = create_clusters()
    max_score = 0
    max_clusters = 0
    max_pred = []
    sub_clusters_arr = []
    num_clusters = 2
    x = 0
    for i in range(0, len(clusters_arr)):
        users_df = create_data.pd.DataFrame(clusters_arr[i]) # users_df = all reshumut of one cluster
        new_users_df = users_df[["sub_category1", "sub_category2", "sub_category3"]]
        new_users_df = (create_data.pd.get_dummies(new_users_df, columns=["sub_category1", "sub_category2", "sub_category3"], prefix_sep='', prefix=''))
        new_users_df = new_users_df.groupby(level=0, axis=1).sum()
        #print(new_users_df)
        clusterer = KMeans(n_clusters=num_clusters, n_init=10).fit(new_users_df[:100])
        cur_pred = clusterer.predict(new_users_df)
        #return cur_pred, users_df, 10
        #cur_sub_clusters_arr = [[] for k in range(num_clusters)]
        cur_sub_clusters_arr = [[] for k in range(num_clusters)]
        for j in range(0, len(cur_pred)):
            cur_sub_clusters_arr[cur_pred[j]].append(users_df.iloc[j])
            #print( str(j) + "cluster:   " , sub_clusters_arr[j])
            x= x+ 1
        sub_clusters_arr.append(cur_sub_clusters_arr)
        
    #for i in range(0, len(sub_clusters_arr)):
       # print(str(i) + " cluster:  ", sub_clusters_arr[i])
    """for i in range(0, len(sub_clusters_arr)):
        pd.set_option('display.max_columns', None)
        print( "cluster " + str(i) + ": ", sub_clusters_arr[i])"""
    # print(sub_clusters_arr[0][0][0]["age"],sub_clusters_arr[0][0][0]["name"],sub_clusters_arr[0][0][0]["city"])
    neo_user.save_in_neo(sub_clusters_arr)
    #print(sub_clusters_arr)
    return sub_clusters_arr


def create_hobbies_clusters():
    clusters_arr = create_sub_clusters()
    print(clusters_arr)
    max_score = 0
    max_clusters = 0
    max_pred = []
    num_clusters = 2
    cur_sub_clusters_arr=[]
    x = 0
    print("length og cluster arr",len(clusters_arr))#super cluster
    print("length of category cluster", len(clusters_arr[0])) #sub
    print("length of category cluster", len(clusters_arr[0][0]))#users_df
    print("length of category cluster", len(clusters_arr[0][0][0]))#users_df properties
    for k in range (len(clusters_arr)): 
        # print("*****************k=",k)
        # print("cluster arr in k:",clusters_arr[k])
        for j in range(len(clusters_arr[k])):
            hobbies_clusters_arr = []
            #print("*****************j=",j)
            # print("clusters arr in k,j:",clusters_arr[k][j])
            users_df = create_data.pd.DataFrame(clusters_arr[k][j]) # users_df = all reshumut of one cluster
            new_users_df = users_df[["hobby1", "hobby2", "hobby3", "age", "region"]]
            new_users_df = (create_data.pd.get_dummies(new_users_df, columns=["hobby1", "hobby2", "hobby3", "region"], prefix_sep='', prefix=''))
            new_users_df = new_users_df.groupby(level=0, axis=1).sum()
            clusterer = KMeans(n_clusters=num_clusters, n_init=10).fit(new_users_df[:100])
            cur_pred = clusterer.predict(new_users_df)
            cur_hobbies_clusters_arr = [[] for p in range(num_clusters)]
            for i in range(0, len(cur_pred)):
                cur_hobbies_clusters_arr[cur_pred[i]].append(users_df.iloc[i])
                x= x + 1
            hobbies_clusters_arr.append(cur_hobbies_clusters_arr)
        cur_sub_clusters_arr.append(hobbies_clusters_arr)
    #neo_user.save_in_neo(cur_sub_clusters_arr)
    print("************************************************************************************************")
    print(cur_sub_clusters_arr)
    return cur_sub_clusters_arr

if __name__ == "__main__":
    #create_hobbies_clusters()
    #predict_data()
    create_clusters()