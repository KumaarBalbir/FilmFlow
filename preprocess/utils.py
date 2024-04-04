import pandas as pd
import numpy as np
import requests
from tmdbv3api import Movie
from tmdbv3api import TMDb
import ast
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()
API_KEY = os.environ.get('API_KEY')

# Initialize TMDb API
tmdb = TMDb()
tmdb.api_key = API_KEY
tmdb_movie = Movie()


def get_genre(movie):
    """
    A function to retrieve the genres of a movie using the TMDb API.
    Args:
        movie (str): The name of the movie to search for.
        API_KEY (str): The API key for accessing the TMDb API.
    Returns:
        str: A string containing the genres of the movie separated by spaces, or np.NaN if the movie is not found or an error occurs.
    """

    try:
        result = tmdb_movie.search(movie)
        if len(result) > 0:
            movie_id = result[0].id
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb.api_key}")
            response.raise_for_status()  # Check for request errors
            json_data = response.json()
            genres_list = json_data.get('genres', [])
            movie_genres = ' '.join(genre.get('name', '')
                                    for genre in genres_list) or np.NaN
            return movie_genres
        else:
            return np.NaN
    except Exception as e:
        print(f"Error for movie '{movie}': {e}")
        return np.NaN


def get_wiki_df(tables):
    """
    A function that takes a list of tables, extracts specific tables from the list, concatenates them, and returns a pandas DataFrame.
    Parameters:
        tables (list): A list of DataFrames representing tables.
    Returns:
        pandas.DataFrame: The concatenated DataFrame.
    """
    if len(tables) >= 6:
        # Perform the append operations
        df1, df2, df3, df4 = tables[2:6]
        df = pd.concat([df1, df2, df3, df4], ignore_index=True)
    else:
        # Handle the case where tables are not available
        df = pd.DataFrame()
    return df


def convert_to_objects(data):
    """
    Convert string representations of lists or dictionaries back into actual Python objects

    Args:
        data (str): The string representation of the data

    Returns:
        object: The converted Python object
    """
    return ast.literal_eval(data)


def get_director(x):
    """
    Function that extracts the director(s) from a string containing movie information.
    Parameters:
    x (str): A string containing movie information.
    Returns:
    str: The extracted director(s) from the input string.
    """
    if " (director)" in x:
        return x.split(" (director);")[0]
    elif " (directors)" in x:
        return x.split(" (directors);")[0]
    else:
        return x.split(" (director/screenplay);")[0]


def get_actor1(x):
    """
    A function that extracts the first actor from a string formatted as "screenplay; actor1, actor2, ..."

    Parameters:
        x (str): The input string containing actors separated by commas after "(screenplay); "

    Returns:
        str: The first actor extracted from the input string, or np.NaN if none is found
    """
    if len((x.split("(screenplay); ")[-1]).split(", ")) >= 1:
        return ((x.split("(screenplay); ")[-1]).split(", ")[0])
    else:
        return np.NaN


def get_actor2(x):
    """
    A function that extracts the second actor from a string separated by "(screenplay);" and ", ".

    Parameters:
    x (str): A string containing actors separated by "(screenplay);" and ", ".

    Returns:
    str: The second actor extracted from the input string. Returns np.NaN if there's no second actor.
    """
    if len((x.split("(screenplay); ")[-1]).split(", ")) >= 2:
        return ((x.split("(screenplay); ")[-1]).split(", ")[1])
    else:
        return np.NaN


def get_actor3(x):
    """
    A function that extracts the third actor from a string if there are at least 3 actors listed after "(screenplay);", otherwise returns np.NaN.

    Parameters:
    x (str): A string containing actor names separated by commas after "(screenplay);"

    Returns:
    str or np.NaN: The third actor listed or np.NaN if there are less than 3 actors.
    """
    if len((x.split("(screenplay); ")[-1]).split(", ")) >= 3:
        return ((x.split("(screenplay); ")[-1]).split(", ")[2])
    else:
        return np.NaN


def get_wiki_process_data(df):
    """
    Generate wiki process data including genres, director, and actor names.

    Parameters:
        df (DataFrame): Input dataframe containing 'Title' and 'Cast and crew' columns.

    Returns:
        DataFrame: Processed dataframe with 'movie_title', 'genres', 'director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name' columns.
    """
    df['genres'] = df['Title'].map(lambda x: get_genre(str(x)))
    df['director_name'] = df['Cast and crew'].map(
        lambda x: get_director(str(x)))
    df['actor_1_name'] = df['Cast and crew'].map(lambda x: get_actor1(str(x)))
    df['actor_2_name'] = df['Cast and crew'].map(lambda x: get_actor2(str(x)))
    df['actor_3_name'] = df['Cast and crew'].map(lambda x: get_actor3(str(x)))
    df = df.loc[:, ['Title', 'genres', 'director_name',
                    'actor_1_name', 'actor_2_name', 'actor_3_name']]
    df = df.rename(columns={'Title': 'movie_title'})
    return df


def get_processed_df1(df1):
    """
    Function to process the input dataframe by selecting specific columns and replacing '|' with ' ' in the 'genres' column.
    Parameters:
    - df1: the input dataframe
    Return:
    - the processed dataframe
    """
    # column subset
    df1 = df1.loc[:, ['movie_title', 'genres', 'director_name',
                      'actor_1_name', 'actor_2_name', 'actor_3_name']]

    # genres are separated via '|', replace it with " "
    df1['genres'] = df1['genres'].str.replace('|', ' ')

    return df1


def get_processed_df2(df2):
    """
    A function to process a DataFrame by selecting specific columns and cleaning the 'id' column.
    """
    df2 = df2.loc[:, ['id', 'genres', 'title']]

    # id column in df2 contains some noise data.

    # is_present = '1997-08-20' in df2['id'].values  returns True.

    # Remove rows where id format is not proper

    # convert non-convertible id values to NaN
    df2['id'] = pd.to_numeric(df2['id'], errors='coerce')

    # Drop rows where 'id' is NaN (i.e., not convertible to int)
    df2 = df2.dropna(subset=['id'])

    # convert id into int
    df2['id'] = df2['id'].astype('int64')


def process_merged_df(df2, df3):
    # Combine df2 and df3
    merged_df = pd.merge(df2, df3, on='id', how='inner')

    merged_df['genres'] = merged_df['genres'].map(convert_to_objects)
    merged_df['cast'] = merged_df['cast'].map(convert_to_objects)
    merged_df['crew'] = merged_df['crew'].map(convert_to_objects)

    merged_df['genres_list'] = merged_df['genres'].apply(
        lambda x: ' '.join([genre.get('name', '') for genre in x]) or np.NaN)

    # actors
    merged_df['actor_1_name'] = merged_df['cast'].apply(
        lambda x: x[0]['name'] if x and len(x) > 0 else np.NaN)
    merged_df['actor_2_name'] = merged_df['cast'].apply(
        lambda x: x[1]['name'] if x and len(x) > 1 else np.NaN)
    merged_df['actor_3_name'] = merged_df['cast'].apply(
        lambda x: x[2]['name'] if x and len(x) > 2 else np.NaN)

    # directors
    merged_df['director_name'] = merged_df['crew'].apply(lambda x: next(
        (crew['name'] for crew in x if crew.get('job') == 'Director'), np.NaN))

    df4 = merged_df.loc[:, ['title', 'genres_list', 'director_name',
                            'actor_1_name', 'actor_2_name', 'actor_3_name']]

    df4 = df4.rename(columns={'title': 'movie_title', 'genres_list': 'genres'})


def get_final_df(df1, df4, df18, df19, df20, df21, df22, df23):

    # Concatenate DataFrames vertically
    df = pd.concat([df1, df4, df18, df19, df20, df21,
                    df22, df23], ignore_index=True)

    df['movie_title'] = df['movie_title'].str.lower()

    # Remove duplicate rows
    df = df.drop_duplicates(subset='movie_title')

    # Resetting the index after dropping duplicates
    df.reset_index(drop=True, inplace=True)

    df.info()

    """Fill missing values as Unknown."""

    df['movie_title'].fillna('unknown', inplace=True)
    df['genres'].fillna('unknown', inplace=True)
    df['director_name'].fillna('unknown', inplace=True)
    df['actor_1_name'].fillna('unknown', inplace=True)
    df['actor_2_name'].fillna('unknown', inplace=True)
    df['actor_3_name'].fillna('unknown', inplace=True)

    """New Feature: combine some features together to hold more context."""

    df['all_info'] = df['actor_1_name'] + ' ' + df['actor_2_name'] + ' ' + \
        df['actor_3_name'] + ' ' + df['director_name'] + ' ' + df['genres']

    return df


def store_csv(df, path):
    df.to_csv(path, index=False)


def get_final_data(df1, df3):
    df3 = df3[["Name", "Genre", "Director", "Actor 1", "Actor 2", "Actor 3"]]
    df3.fillna("unknown", inplace=True)

    df3 = df3.rename(columns={"Name": "movie_title", "Genre": "genres", "Director": "director_name",
                     "Actor 1": "actor_1_name", "Actor 2": "actor_2_name", "Actor 3": "actor_3_name"})
    df3["all_info"] = df3["genres"] + " " + df3["director_name"] + " " + \
        df3["actor_1_name"] + " " + \
        df3["actor_2_name"] + " " + df3["actor_3_name"]

    df = pd.concat([df1, df3], ignore_index=True)

    df['movie_title'] = df['movie_title'].str.lower()

    # Remove duplicate rows
    df = df.drop_duplicates(subset='movie_title')

    # Resetting the index after dropping duplicates
    df.reset_index(drop=True, inplace=True)
    return df


def clean_data(data):
    # Remove punctuation and other unwanted characters from movie_title and all_info columns
    data['movie_title'] = data['movie_title'].apply(
        lambda x: re.sub(r'[^\w\s]', '', x))
    data['all_info'] = data['all_info'].apply(
        lambda x: re.sub(r'[^\w\s]', '', x))

    # Convert HTML entities to regular characters
    data['movie_title'] = data['movie_title'].apply(html.unescape)
    data['all_info'] = data['all_info'].apply(html.unescape)

    # Remove leading and trailing whitespace from movie_title
    data['movie_title'] = data['movie_title'].str.strip()

    # Convert all characters to lowercase
    data['movie_title'] = data['movie_title'].str.lower()
    data['all_info'] = data['all_info'].str.lower()

    return data
