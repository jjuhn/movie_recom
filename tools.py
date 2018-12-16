import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from movie_rec import users, ratings, items


# joining ratings and items to include movie name and ratings.
movie_ratings = pd.merge(ratings, items, left_on=ratings['movie_id'], right_on=items['movie_id'], how='right')

user_movie_ratings = pd.merge(users, ratings, left_on=users['user_id'], right_on=ratings['user_id'], how='inner')
user_movie_ratings.rename(columns={'key_0': 'user_id'}, inplace=True)
user_movie_ratings = user_movie_ratings[["user_id", "age", "sex", "occupation", "movie_id", "rating"]]

# getting average ratings for movies it will be used for displaying the movies in /movies
ratings_avg = ratings.groupby(ratings.movie_id, as_index=False).mean()
movie_ratings_avg = pd.merge(ratings_avg, items, left_on=ratings_avg['movie_id'], right_on=items['movie_id'], how='right')
movie_ratings_sorted = movie_ratings_avg[['movie title', 'release date', 'rating']].sort_values(['rating', 'release date'], ascending=[0,0])

# getting the number of unique users
n_users = ratings.user_id.unique().shape[0]
# getting the number of unique movies
n_movies = ratings.movie_id.unique().shape[0]
# getting the unique number of occupations
n_occupations = users.occupation.unique().shape[0]


# grouping the user_movie_rating table by age group and converts it into categorical codes
user_movie_ratings["age_group"] = pd.cut(user_movie_ratings["age"], bins=[0, 10, 20, 30, 40, 50, 60, 70, 120], labels=[0,10,20,30,40,50,60,70])
user_movie_ratings['age_code'] = user_movie_ratings.age_group.astype('category').cat.codes

# getting the unique number of age group
n_age_group = user_movie_ratings.age_group.unique().shape[0]

# just prompting out
print 'Number of users = ' + str(n_users) + ' | Number of movies = ' + str(n_movies) + "" \
      + " | Number of Age group = " + str(n_age_group) + ' | Number of occupations = ' + str(n_occupations)

# create a pivot table based on user_id, age_group and occupations
Ratings = ratings.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
user_movie_ratings_age_group = user_movie_ratings.groupby(['age_group', 'movie_id'], as_index=False).mean().dropna()
user_movie_ratings_occupation = user_movie_ratings.groupby(['occupation', 'movie_id'], as_index=False).mean().dropna()
Ratings_age = user_movie_ratings_age_group.pivot(index='age_group', columns='movie_id', values='rating').fillna(0)
Ratings_occ = user_movie_ratings_occupation.pivot(index='occupation', columns='movie_id', values='rating').fillna(0)

# I just wanted to check for sparsity.
# sparsity = round(1.0 - len(ratings) / float(n_users * n_movies), 3)
# print 'The sparsity level of MovieLens1M dataset is ' + str(sparsity * 100) + '%'

def get_all_predicted_ratings(ratings, k):
    '''

    :param ratings: pivot table of dataframe of ratings.  it could be user based rating, age based or occupation based
    :param k: latent factors must be smaller than the category
    :return: predictions of movie ratings of all users, age or occupations in dataframe
    '''

    # converting the pivot table into matrices for user_id, age and occupation
    R = ratings.as_matrix()
    # getting the mean of pivot table by the column
    ratings_mean = np.mean(R, axis=1)
    # subtracting the mean from the original matrices
    Ratings_demeaned = R - ratings_mean.reshape(-1, 1)
    columns = Ratings.columns

    # using the svds package from the scipy
    U, sigma, Vt = svds(Ratings_demeaned, k=k)
    sigma = np.diag(sigma)
    all_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + ratings_mean.reshape(-1, 1)
    predictions = pd.DataFrame(all_predicted_ratings, columns=columns)

    return predictions

preds_ratings = get_all_predicted_ratings(Ratings, 50)
preds_age_group = get_all_predicted_ratings(Ratings_age, 7)
preds_occupation = get_all_predicted_ratings(Ratings_occ, 20)


def recommend_movies(predictions, userID, movies, original_ratings, num_recommendations):
    '''

    :param predictions: predictions, it has to be user based prediction
    :param userID: user id from user's response
    :param movies: original movies dataframe
    :param original_ratings: orignal ratings dataframe
    :param num_recommendations: number of recommendation to display
    :return: user_full: already rated movies by user_id, recommendations: recommended movies for this user
    '''
    # Get and sort the user's predictions
    user_row_number = userID - 1  # User ID starts at 1, not 0
    sorted_user_predictions = predictions.iloc[user_row_number].sort_values(ascending=False)  # User ID starts at 1

    # Get the user's data and merge in the movie information.
    user_data = original_ratings[original_ratings.user_id == (userID)]
    user_full = (user_data.merge(movies, how='left', left_on='movie_id', right_on='movie_id').
                 sort_values(['rating'], ascending=False)
                 )

    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies[~movies['movie_id'].isin(user_full['movie_id'])].
                           merge(pd.DataFrame(sorted_user_predictions).reset_index(), how='left',
                                 left_on='movie_id',
                                 right_on='movie_id').
                           rename(columns={user_row_number: 'Predictions'}).
                           sort_values('Predictions', ascending=False).
                           iloc[:num_recommendations, :-1]
                           )

    return user_full, recommendations


def show_movies_by_age_group(age_group, num):
    '''

    :param age_group: age group is a integer 1 means 10 - 20 years old. etc.
    :param num: number of records to be returned
    :return: sorted results of movies with high ratings in this age_group.  Can be misleading because it did not normalize the count.
    '''
    age_group = age_group * 10
    movies = user_movie_ratings_age_group[user_movie_ratings_age_group["age_group"] == age_group]
    m_movies = pd.merge(movies, items, left_on=movies['movie_id'], right_on=items['movie_id'], how='inner')

    return m_movies.sort_values('rating', ascending=False)[['movie_id_x', 'movie title', 'release date']][:num]

def show_movies_by_occ(occupation, num):
    '''

    :param occupation: occupation in string
    :param num: number of records to be returned
    :return: sorted results of movies with high ratings in given occupation.
    '''
    movies = user_movie_ratings_occupation[user_movie_ratings_occupation["occupation"]==occupation]
    m_movies = pd.merge(movies, items, left_on=movies['movie_id'], right_on=items['movie_id'], how='inner')

    return m_movies.sort_values('rating', ascending=False)[['movie_id_x', 'movie title', 'release date']][:num]


def recommend_movies_by_age_group(predictions, age_group, movies, original, num_recommendations):
    '''

    :param predictions: age based prediction dataframe for all age group
    :param age_group: age_group in integer.
    :param movies: movies dataframe
    :param original: original ratings
    :param num_recommendations: number of recommendations
    :return: dataframe of ranked sorted movies based on the age group.
    '''
    sorted_age_predictions = predictions.iloc[age_group].sort_values(ascending=False)

    sorter = list(sorted_age_predictions.index)
    sorterIndex = dict(zip(sorter, range(len(sorter))))

    rank_movies = movies.copy()
    rank_movies['rank'] = rank_movies['movie_id'].map(sorterIndex)
    rank_movies.sort_values(by=['rank'])

    return rank_movies.sort_values(by=['rank'])[:num_recommendations]



def recommend_movies_by_occupation(predictions, occupation, movies, num_recommendations):
    '''

    :param predictions: occupation based prediction dataframe for all occupations
    :param occupation: user given occupation
    :param movies: movies data frame
    :param num_recommendations: number of recommendations
    :return: data frame of ranked sorted movies based on the occupations
    '''
    sorted_occ_predictions = predictions.iloc[occupation].sort_values(ascending=False)
    sorter = list(sorted_occ_predictions.index)
    sorterIndex = dict(zip(sorter, range(len(sorter))))
    rank_movies = movies.copy()
    rank_movies['rank'] = rank_movies['movie_id'].map(sorterIndex)
    rank_movies.sort_values(by=['rank'])

    return rank_movies.sort_values(by=['rank'])[:num_recommendations]

