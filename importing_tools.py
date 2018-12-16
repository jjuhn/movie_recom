import os
import pandas as pd


def read_files():
    filepath = os.path.abspath(os.path.dirname(__file__))
    userpath = os.path.join(filepath, 'data/ml-100k/u.user')
    ratingspath = os.path.join(filepath, 'data/ml-100k/u.data')
    itemspath = os.path.join(filepath, 'data/ml-100k/u.item')

    # Reading users file:
    u_cols = ['user_id', 'age', 'sex', 'occupation', 'zipcode']
    users = pd.read_csv(userpath, sep='|', names=u_cols, encoding='latin-1')

    # Reading ratings file:
    r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
    ratings = pd.read_csv(ratingspath, sep='\t', names=r_cols,
                          encoding='latin-1')

    # Reading items file:
    i_cols = ['movie_id', 'movie title', 'release date', 'video release date', 'IMDb URL', 'unknown', 'Action',
              'Adventure',
              'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
              'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    items = pd.read_csv(itemspath, sep='|', names=i_cols,
                        encoding='latin-1')

    return users, ratings, items
