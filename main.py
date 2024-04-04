import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests

# Load environment variables from .env file
load_dotenv()

API_KEY = os.environ.get('API_KEY')



# global avialbe variable
data = pd.read_csv('./data/final_data.csv', nrows=5000)

# creating a count matrix
cv = CountVectorizer()
count_matrix = cv.fit_transform(data['all_info'])
# creating a similarity score matrix
similarity = cosine_similarity(count_matrix)


# load the nlp model and tfidf vectorizer from disk
filename = 'artifact/sentiment_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('artifact/transform.pkl', 'rb'))


# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])


def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/titles")
def titles():
    titles = list(data['movie_title'].str.capitalize())

    # Convert HTML entities to regular characters
    # titles = [html.unescape(title) for title in titles]
    return jsonify(titles)


# Create an endpoint to proxy requests to external APIs
@app.route("/proxy", methods=["GET"])
def proxy_request():
    # Get the URL and params from the query parameters
    params = request.args.get('params')

    # Convert params to a dictionary
    params_dict = json.loads(params)

    url = params_dict['URL']

    # Add api key
    params_dict['api_key'] = API_KEY

    # Make the request to the external API with the API key
    response = requests.get(url, params=params_dict)

    # Return the response from the external API to the client
    return jsonify(response.json())


@app.route("/similar", methods=["POST"])
def similar():
    try:
        # Get the JSON data from the request
        dat = request.get_json()
        title = dat[0].get("query")

        movies_list = list(data['movie_title'].str.capitalize())

        if title not in movies_list:
            return jsonify({'error': 'Oops! The movie you requested is not in our records. Please make sure the spelling is correct or try with some other movies'}), 404
        else:

            idx = data.loc[data['movie_title'].str.capitalize()
                           == title].index[0]

            lst = list(enumerate(similarity[idx]))

            sorted_list = sorted(lst, key=lambda x: x[1], reverse=True)

            # excluding first item since it is the requested movie itself
            lst = sorted_list[1:11]

            similar_movies = []
            for index in range(len(lst)):
                a = lst[index][0]
                similar_movies.append(data['movie_title'][a])

            # Send just the top 10 most similar movie titles

            print("similar movies", similar_movies)
            return jsonify(similar_movies[:10])
    except Exception as e:
        # Handle any exceptions gracefully
        print("Error in similar route:", e)
        return jsonify({'error': 'An error occurred while processing the request'}), 500


@app.route("/movie_id", methods=["POST"])
def movie_id():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        url = data[0].get("URL")
        title = data[0].get("query")
        params = {
            'api_key': API_KEY,
            'query': title}

        # Make the request to the external API with the API key
        response = requests.get(url, params=params)
        return jsonify(response.json())

    except Exception as e:
        # Handle any exceptions gracefully
        print("Error in movie_id route:", e)
        return jsonify({'error': 'An error occurred while processing the request'}), 500


@app.route("/MovieCastes", methods=["POST"])
def MovieCastes():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        url = data[0].get("URL")

        # Make the request to the external API with the API key
        response = requests.get(url, {'api_key': API_KEY})
        return jsonify(response.json())

    except Exception as e:
        # Handle any exceptions gracefully
        print("Error in movie_id route:", e)
        return jsonify({'error': 'An error occurred while processing the request'}), 500


@app.route("/CastesDetails", methods=["POST"])
def CastesDetails():
    data = request.get_json()
    url = data[0].get("URL")
    # Make the request to the external API with the API key
    response = requests.get(url, {'api_key': API_KEY})

    return jsonify(response.json())


@app.route("/recommend", methods=["POST"])
def recommend():
    # getting data from AJAX request
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    rec_movies = request.form['recommended_movies']
    rec_posters = request.form['posters']

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)

    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)

    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[", "")
    cast_ids[-1] = cast_ids[-1].replace("]", "")

    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: rec_movies[i]
                   for i in range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i],
                             cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i],
                                    cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    # web scraping to get user reviews from IMDB site
    sauce = urllib.request.urlopen(
        'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    soup_result = soup.find_all("div", {"class": "text show-more__control"})

    reviews_list = []  # list of reviews
    reviews_status = []  # list of comments (good or bad)
    for reviews in soup_result:
        if reviews.string:
            reviews_list.append(reviews.string)
            # passing the review to our model
            movie_review_list = np.array([reviews.string])
            movie_vector = vectorizer.transform(movie_review_list)
            pred = clf.predict(movie_vector)
            reviews_status.append('Good' if pred else 'Bad')

    # combining reviews and comments into a dictionary
    movie_reviews = {reviews_list[i]: reviews_status[i]
                     for i in range(len(reviews_list))}

    # passing all the data to the html file
    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           release_date=release_date, runtime=runtime,  genres=genres,
                           movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)


if __name__ == '__main__':
    app.run(debug=True)
