# Import utils functions
from preprocess.utils import get_wiki_process_data
from preprocess.utils import get_wiki_df
from preprocess.utils import get_processed_df1
from preprocess.utils import get_processed_df2
from preprocess.utils import process_merged_df
from preprocess.utils import get_final_df
from preprocess.utils import store_csv

# import libraries
import pandas as pd
import numpy as np


df1 = pd.read_csv("../data/movie_metadata.csv")
df2 = pd.read_csv("../data/movies_metadata.csv")
df3 = pd.read_csv("../data/credits.csv")

# Links of wikipedia tables

link18 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2018"
link19 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2019"
link20 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2020"
link21 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2021"
link22 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2022"
link23 = "https://en.wikipedia.org/wiki/List_of_American_films_of_2023"

# Read the tables
tables18 = pd.read_html(link18, header=0)  # year 2018
tables19 = pd.read_html(link19, header=0)  # year 2019
tables20 = pd.read_html(link20, header=0)  # year 2020
tables21 = pd.read_html(link21, header=0)  # year 2021
tables22 = pd.read_html(link22, header=0)  # year 2022
tables23 = pd.read_html(link23, header=0)  # year 2023


df18 = get_wiki_df(tables18)
df19 = get_wiki_df(tables19)
df20 = get_wiki_df(tables20)
df21 = get_wiki_df(tables21)
df22 = get_wiki_df(tables22)
df23 = get_wiki_df(tables23)


# Process df1
df1 = get_processed_df1(df1)


# Process df2
df2 = get_processed_df2(df2)


# Process combined df2 and df3
df4 = process_merged_df(df2, df3)


# Process 2018 Movies

df18 = get_wiki_process_data(df18)

# Process 2019 Movies

df19 = get_wiki_process_data(df19)

# Process 2020 Movies

df20 = get_wiki_process_data(df20)

# Process 2021 Movies

df21 = get_wiki_process_data(df21)

# Process 2022 Movies

df22 = get_wiki_process_data(df22)

# Process 2023 Movies

df23 = get_wiki_process_data(df23)


# Merge and Clean final dataframes
# We get first level clean data as df1, df4 (got from df2 and df3), df18 to df23.
# Lets merge it to a single df and preprocess that.
df = get_final_df(df1, df4, df18, df19, df20, df21, df22, df23)


# store to csv
store_csv(df, '../data/data.csv')
