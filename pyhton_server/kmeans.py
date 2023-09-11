from main import neo_user
import string
import warnings
import mssql
import pandas as pd
# This imports the KMeans clustering algorithm from the scikit-learn library,
# which is used for machine learning tasks such as clustering, classification, and regression.
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MaxAbsScaler

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from nltk.tokenize import TweetTokenizer

import matplotlib.pyplot as plt
import create_data
import contractions
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
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
create_data.pd.set_option('display.max_colwidth', None)  # Set the option to show the full contents of a column
import warnings  # Import warnings again to filter UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.feature_extraction.text")  # Suppress UserWarning

def save_usercredentials_sql(users_df):
    #saving users' email and password and usernum in mssql database
    users_credentials_array = []
    for index, row in users_df.iterrows():
        users_credentials_array.append((row["user_num"], row["email"], row["password"]))
        mssql.save_in_sqldb(users_credentials_array)
  
def predict_data():
    # Firstly, this method checks if neo4j database is empty. 
    # If it's empty, it means this is the first time we run the app - so we fetch the users' data from a csv file and save it in neo4j database
    # If it's not empty, it means the initial users have already been loaded to the databases. this case is uses to update the database and run the algorithm again.
    if (neo_user.is_database_empty()):
        print("Database is empty, adding all users")
        users_df = create_data.pd.read_csv("newdata.csv", low_memory=False)
        users_df = users_df.head(500)
        #save the email + passwords to SQL
        save_usercredentials_sql(users_df) 
    else:
        print("Database is not empty, adding/updating new user")
        users_df = neo_user.get_all_users_df()
    return users_df
        
def process_data(users_df = create_data.pd.DataFrame()):
    # Process user data for text analysis.
    # This function tokenizes and preprocesses the text data from the 'hobby' column in the provided DataFrame. It performs tasks such as:
    # - Tokenization using TweetTokenizer
    # - Handling contractions in text
    # - Removing stopwords and lemmatization
    # - Filtering out non-sentimental text
    # - Combining processed tokens into a single string
    stop_words = set(stopwords.words('english'))
    # This defines a list of costume stop words that are added to the existing set of stop words.
    # Read the stop words from the file
    with open('stopwords.txt', 'r',encoding='utf-8') as f:
        custom_stopwords = [word.strip() for word in f]
    stop_words.update(custom_stopwords)

    if(users_df.empty):
        print(users_df)
        users_df = predict_data()
    processed_data = []
    # Define the lemmatizer object, which will be used later to lemmatize the words in the text data.
    # it involves removing the inflectional endings of words and converting them into a common base or root form.
    # This process helps to reduce the number of unique words in the text data,
    # and can also improve the accuracy of analysis by grouping together words with similar meanings.
    # For example, the words "am", "are", "is" can all be lemmatized to "be",
    # and the words "walk", "walking", "walked" can all be lemmatized to "walk".
    lemmatizer = WordNetLemmatizer()
    tweet_tokenizer = TweetTokenizer()
    sid = SentimentIntensityAnalyzer()

    # This line iterates through each row of the users_df DataFrame,
    # where index represents the index of the row and row represents the actual row data.
    for index, row in users_df.iterrows():
        hobbies = re.split(r'\s+', row['hobby'])
        punctuation = string.punctuation
        punctuation = punctuation.replace("'", '')
        hobbies = [h.rstrip(punctuation).strip().lower() for h in hobbies]
        hobbies = [h.strip().lower() for h in hobbies]
        processed_hobbies = []
        for hobby in hobbies:
            sentiment_scores = sid.polarity_scores(hobby)
            if sentiment_scores['pos'] < 0.1 and sentiment_scores['neg'] < 0.1:
                tokens = tweet_tokenizer.tokenize(hobby)
                tokens = [contractions.fix(token) for token in tokens]
                processed_tokens = []
                for token in tokens:
                    if ' ' in token:
                        split_tokens = token.split(' ')
                        processed_tokens.extend(split_tokens)
                    else:
                        processed_tokens.append(token)
                processed_tokens = [token for token in processed_tokens if token not in stop_words]
                processed_tokens = [lemmatizer.lemmatize(token) for token in processed_tokens]
                processed_hobby = ' '.join(token for token in processed_tokens if token)
                processed_hobbies.append(processed_hobby)
        hobbies = ' '.join(processed_hobbies)
        hobbies = re.sub('\s+', ' ', hobbies).strip()
        processed_data.append(hobbies)
    return(processed_data,tweet_tokenizer)

def custom_tokenizer(text, tweet_tokenizer):
    tokens = tweet_tokenizer.tokenize(text)  # Use your preferred tokenizer
    return tokens

def countvector():
    # Create a custom tokenizer for text data.
    # This function uses the provided TweetTokenizer object to tokenize the input text, returning a list of tokens.
    processed_data, tweet_tokenizer =process_data()
    count_vectorizer = CountVectorizer(tokenizer=lambda text: custom_tokenizer(text, tweet_tokenizer), token_pattern=r'\b\w+\b|\w+-\w+')
    count_matrix = count_vectorizer.fit_transform(processed_data)
    return count_matrix, count_vectorizer

def topic_clustering():
    # Perform topic modeling using Latent Dirichlet Allocation (LDA).
    # This function applies Latent Dirichlet Allocation (LDA) to the text data after vectorization using CountVectorizer.
    # It identifies topics within the text and filters user data based on topic-related keywords.
    count_matrix, count_vectorizer = countvector()
    n_topics = 12
    lda = LatentDirichletAllocation(n_components=n_topics, max_iter=50,
                                    learning_method='batch',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(count_matrix)
    

    # Use Latent Dirichlet Allocation (LDA) to identify the most relevant topics in the text
    #  LDA is a probabilistic model that discovers underlying topics in a collection of text data by clustering words that frequently occur together.
    #  Here, n_topics specifies the number of topics to be identified, and lda is an instance of the LDA model that is fit to the TF-IDF matrix.

    # Get the topic-word matrix from the LDA model
    topic_word_matrix = lda.components_

    # Get the feature names (words) from the CountVectorizer
    feature_names = count_vectorizer.get_feature_names_out()
    n_top_words = 10  # Define the number of top words to display for each topic
    for topic_idx, topic in enumerate(topic_word_matrix):
        top_words_idx = create_data.np.argsort(topic)[::-1][:n_top_words]  # Get the indices of the top words
        top_words = [feature_names[i] for i in top_words_idx]  # Get the actual words

    #Generate candidate keywords by selecting the top words from each topic
    # These lines of code generate candidate keywords by selecting the top words from each topic identified by the LDA model.
    # It iterates through each topic, sorts the words in descending order of importance, selects the top 10 words,
    # and adds them to the keywords list.
    keywords = []
    for topic_idx, topic in enumerate(lda.components_):
        top_keywords_idx = topic.argsort()[::-1][:100]
        top_keywords = [count_vectorizer.get_feature_names_out()[i] for i in top_keywords_idx]
        keywords.extend(top_keywords)

    ## Remove duplicate keywords
    keywords = list(set(keywords))

    # Create a filter for the keywords
    keyword_filter = '|'.join(keywords)

    # Filter the hobbies based on the keywords
    users_df = predict_data()
    users_df['filtered_hobbies'] = users_df['hobby'].str.lower().str.findall(keyword_filter).apply(
        lambda x: ', '.join(x))

    filtered_count_matrix = count_vectorizer.transform(users_df['filtered_hobbies'])

    # Scale the features
    scaler = MaxAbsScaler()
    scaled_count_matrix = scaler.fit_transform(filtered_count_matrix)

    # Apply dimensionality reduction using TruncatedSVD
    svd = TruncatedSVD(n_components=22)
    reduced_features = svd.fit_transform(scaled_count_matrix)
    return(reduced_features, filtered_count_matrix, users_df)
    
def kmeansclustering():
    # Perform KMeans clustering on user data.
    # This function applies KMeans clustering to the reduced features of user data obtained from topic modeling. 
    # It identifies clusters of users based on their interests and updates or adds them to a Neo4j database.
    emptyDbFlag=False;
    if (neo_user.is_database_empty()):
        emptyDbFlag=True;
    
    reduced_features, filtered_count_matrix, users_df = topic_clustering()
    km_scores = {}
    n_clusters_range = range(15, 30)
    wcss = []

    for n_clusters in n_clusters_range:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto')
        kmeans.fit(reduced_features)
        wcss.append(kmeans.inertia_)

    # Determine the elbow point, which is the point of maximum curvature in the WCSS curve
    wcss_diff = create_data.np.diff(wcss)
    curvature = create_data.np.diff(wcss_diff)
    elbow_point = n_clusters_range[create_data.np.argmax(curvature) + 1]

    # Cluster the users based on their filtered hobbies using the optimal number of clusters
    kmeans = KMeans(n_clusters=elbow_point, random_state=0, n_init='auto')
    kmeans.fit(filtered_count_matrix)

    # Assign each user to a cluster based on the cosine similarity between their count vector and the cluster centers
    users_df['cluster'] = kmeans.predict(filtered_count_matrix)
    cluster_centers = kmeans.cluster_centers_

    # Compute the cosine similarity between each user's count vector and the cluster centers
    similarity_matrix = cosine_similarity(filtered_count_matrix, cluster_centers)

    # Find the index of the cluster center that has the highest similarity for each user
    cluster_indices = create_data.np.argmax(similarity_matrix, axis=1)

    # Assign the cluster label to each user based on the index of the most similar cluster center
    users_df['cluster'] = cluster_indices

    # The purpose of the line len(users_df[users_df['cluster'] == cluster]) == 0 is to check whether there are any users in the current cluster. If there are no users in the cluster, then the code will break out of the loop and stop printing clusters.
    # Print the users in each cluster
    for cluster in range(n_clusters):
        if cluster >= elbow_point and len(users_df[users_df['cluster'] == cluster]) == 0:
            break  # Stop printing clusters after the elbow point with no people in them
        cluster_users = users_df[users_df['cluster'] == cluster]
        print(f"Cluster {cluster}:")
        for index, row in cluster_users.iterrows():
            print(f"- {row['name']}, {row['hobby']}")
        print("\n")
    
    if(emptyDbFlag):
        neo_user.addAll(elbow_point, users_df, cluster_centers)
    else:
        neo_user.updateAll(users_df, cluster_centers)
