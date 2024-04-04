# import utils functions
from preprocess.utils import store_csv
from preprocess.utils import get_final_data
from preprocess.utils import clean_data

# import libraries
import pandas as pd
import chardet

df1 = pd.read_csv("../data/data.csv")
df2 = pd.read_csv("../data/BollywoodMovieDetail.csv")


# Detect encoding for the problematic file
with open("../data/IMDb Movies India.csv", 'rb') as f:
    result = chardet.detect(f.read())

# Use the detected encoding
df3 = pd.read_csv("../data/IMDb Movies India.csv", encoding=result['encoding'])


# df2['releaseYear'].unique()

# df3['Year'].unique()

# Just process df3 it has already movies from the year present in df2.


df = get_final_data(df1, df3)

# clean data
df = clean_data(df)
# save df to csv
store_csv(df, "../data/final_data.csv")
