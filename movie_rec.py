from flask import Flask
from flask import render_template, url_for, redirect, flash
import pandas as pd
import os
from forms import ExistingUserForm, NewUserForm
import numpy as np
from scipy.sparse.linalg import svds

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my big secret'

filepath = os.path.abspath(os.path.dirname(__file__))
userpath = os.path.join(filepath, 'data/ml-100k/u.user')
ratingspath = os.path.join(filepath, 'data/ml-100k/u.data')
itemspath = os.path.join(filepath, 'data/ml-100k/u.item')

#Reading users file:
u_cols = ['user_id', 'age', 'sex', 'occupation', 'zipcode']
users = pd.read_csv(userpath, sep='|', names=u_cols, encoding='latin-1')

#Reading ratings file:
r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
ratings = pd.read_csv(ratingspath, sep='\t', names=r_cols,
 encoding='latin-1')

#Reading items file:
i_cols = ['movie_id', 'movie title' ,'release date','video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure',
 'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
items = pd.read_csv(itemspath, sep='|', names=i_cols,
 encoding='latin-1')


# movie and ratings
movie_ratings = pd.merge(ratings, items, left_on=ratings['movie_id'], right_on=items['movie_id'], how='right')
# Avg
ratings_avg = ratings.groupby(ratings.movie_id, as_index=False).mean()
movie_ratings_avg = pd.merge(ratings_avg, items, left_on=ratings_avg['movie_id'], right_on=items['movie_id'], how='right')
movie_ratings_sorted = movie_ratings_avg[['movie title', 'release date', 'rating']].sort_values(['rating', 'release date'], ascending=[0,0])


# user demographic information and the ratings
user_movie_ratings = pd.merge(users, ratings, left_on=users['user_id'], right_on=ratings['user_id'], how='inner')

user_movie_ratings.rename(columns={'key_0': 'user_id'}, inplace=True)
user_movie_ratings = user_movie_ratings[["user_id", "age", "sex", "occupation", "movie_id", "rating"]]


n_users = ratings.user_id.unique().shape[0]
n_movies = ratings.movie_id.unique().shape[0]
user_movie_ratings["age_group"] = pd.cut(user_movie_ratings["age"], bins=[0, 10, 20, 30, 40, 50, 60, 70, 120], labels=[0,10,20,30,40,50,60,70])
user_movie_ratings['age_code'] = user_movie_ratings.age_group.astype('category').cat.codes

n_occupations = users.occupation.unique().shape[0]
n_age_group = user_movie_ratings.age_group.unique().shape[0]


print 'Number of users = ' + str(n_users) + ' | Number of movies = ' + str(n_movies) + "" \
      + " | Number of Age group = " + str(n_age_group) + ' | Number of occupations = ' + str(n_occupations)


Ratings = ratings.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)

# group by age and movie id in order to create pivot table.
user_movie_ratings_age_group = user_movie_ratings.groupby(['age_group', 'movie_id'], as_index=False).mean().dropna()

user_movie_ratings_occupation = user_movie_ratings.groupby(['occupation', 'movie_id'], as_index=False).mean().dropna()

user_movie_ratings_gender = user_movie_ratings.groupby(['sex', 'movie_id'], as_index=False).mean()


Ratings_age = user_movie_ratings_age_group.pivot(index='age_group', columns='movie_id', values='rating').fillna(0)
Ratings_occ = user_movie_ratings_occupation.pivot(index='occupation', columns='movie_id', values='rating').fillna(0)
Ratings_gender = user_movie_ratings_gender.pivot(index='sex', columns='movie_id', values='rating').fillna(0)

R = Ratings.as_matrix()
R_age = Ratings_age.as_matrix()
R_occ = Ratings_occ.as_matrix()
R_gender = Ratings_gender.as_matrix()


user_ratings_mean = np.mean(R, axis=1)
age_ratings_mean = np.mean(R_age, axis=1)
occ_ratings_mean = np.mean(R_occ, axis=1)
gender_ratings_mean = np.mean(R_gender, axis=1)


Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)
Ratings_age_demeaned = R_age - age_ratings_mean.reshape(-1, 1)
Ratings_occ_demeaned = R_occ - occ_ratings_mean.reshape(-1, 1)
Ratings_gender_demeaned = R_gender - gender_ratings_mean.reshape(-1, 1)


sparsity = round(1.0 - len(ratings) / float(n_users * n_movies), 3)
print 'The sparsity level of MovieLens1M dataset is ' + str(sparsity * 100) + '%'



def get_all_predicted_ratings(demeaned, ratings_mean, k, columns):
    U, sigma, Vt = svds(demeaned, k=k)
    sigma = np.diag(sigma)
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + ratings_mean.reshape(-1, 1)
    preds = pd.DataFrame(all_user_predicted_ratings, columns=columns)

    return preds

preds_ratings = get_all_predicted_ratings(Ratings_demeaned, user_ratings_mean, k=50, columns=Ratings.columns)
preds_age_group = get_all_predicted_ratings(Ratings_age_demeaned, age_ratings_mean, k=7, columns=Ratings_age.columns)
preds_occupation = get_all_predicted_ratings(Ratings_occ_demeaned, occ_ratings_mean, k=20, columns=Ratings_occ.columns)
preds_gender = get_all_predicted_ratings(Ratings_gender_demeaned, gender_ratings_mean, k=1, columns=Ratings_gender.columns)


def show_movies_by_age_group(age_group, num):
    age_group = age_group * 10
    movies = user_movie_ratings_age_group[user_movie_ratings_age_group["age_group"] == age_group]
    m_movies = pd.merge(movies, items, left_on=movies['movie_id'], right_on=items['movie_id'], how='inner')

    return m_movies.sort_values('rating', ascending=False)[['movie_id_x', 'movie title', 'release date']][:num]

def recommend_movies_by_age_group(predictions, age_group, movies, original, num_recommendations):
    sorted_age_predictions = predictions.iloc[age_group].sort_values(ascending=False)

    sorter = list(sorted_age_predictions.index)
    sorterIndex = dict(zip(sorter, range(len(sorter))))

    rank_movies = movies.copy()
    rank_movies['rank'] = rank_movies['movie_id'].map(sorterIndex)
    rank_movies.sort_values(by=['rank'])

    return rank_movies.sort_values(by=['rank'])[:num_recommendations]

def show_movies_by_occ(occupation, num):
    movies = user_movie_ratings_occupation[user_movie_ratings_occupation["occupation"]==occupation]
    m_movies = pd.merge(movies, items, left_on=movies['movie_id'], right_on=items['movie_id'], how='inner')

    return m_movies.sort_values('rating', ascending=False)[['movie_id_x', 'movie title', 'release date']][:num]


def recommend_movies_by_occupation(predictions, occupation, movies, num_recommendations):
    sorted_occ_predictions = predictions.iloc[occupation].sort_values(ascending=False)
    sorter = list(sorted_occ_predictions.index)
    sorterIndex = dict(zip(sorter, range(len(sorter))))
    rank_movies = movies.copy()
    rank_movies['rank'] = rank_movies['movie_id'].map(sorterIndex)
    rank_movies.sort_values(by=['rank'])

    return rank_movies.sort_values(by=['rank'])[:num_recommendations]

def recommend_movies_by_gender(predictions, gender, movies, num_recommendations):
    sorted_gender_predictions = predictions.iloc[gender].sort_values(ascending=False)
    sorter = list(sorted_gender_predictions.index)
    sorterIndex = dict(zip(sorter, range(len(sorter))))

    rank_movies = movies.copy()
    rank_movies['rank'] = rank_movies['movie_id'].map(sorterIndex)
    rank_movies.sort_values(by=['rank'])

    return rank_movies.sort_values(by=['rank'])[:num_recommendations]


def recommend_movies(predictions, userID, movies, original_ratings, num_recommendations):
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

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/movies')
def movies():

    return render_template('movies.html', items=movie_ratings_sorted.to_html())

@app.route('/existing', methods=['GET', 'POST'])
def existingUser():
    form = ExistingUserForm()

    if form.validate_on_submit():
        movies_rated_by_user_id = movie_ratings[movie_ratings.user_id == form.userID.data]

        html_table_movies_rated_by_user_id = movies_rated_by_user_id[['movie_id_x', 'movie title', 'release date', 'rating']].sort_values(by='rating', ascending=False).to_html()

        already_rated, predictions = recommend_movies(preds_ratings, int(form.userID.data), items, ratings, 20)

        return render_template('show_user.html', uID=form.userID.data, movies=html_table_movies_rated_by_user_id,
                               recommendation=predictions[['movie_id', 'movie title', 'release date']].to_html())
    else:
        if form.errors:
            flash(message=form.errors.values())
        return render_template('existing.html', form=form)


@app.route('/new_user', methods=['GET', 'POST'])
def newUser():
    form = NewUserForm()
    if form.validate_on_submit():
        a = int(form.age.data)
        if a < 10:
            a = 0
        elif a >= 10 and a < 20:
            a = 1
        elif a >= 20 and a < 30:
            a = 2
        elif a >= 30 and a < 40:
            a = 3
        elif a >= 40 and a < 50:
            a = 4
        elif a >= 50 and a < 60:
            a = 5
        elif a >= 60 and a < 70:
            a = 6
        elif a >= 70:
            a = 7

        occ_dict = {0: 'administrator',
        1: 'artist',
        2: 'doctor',
        3: 'educator',
        4: 'engineer',
        5: 'entertainment',
        6: 'executive',
        7: 'healthcare',
        8: 'homemaker',
        9: 'lawyer',
        10: 'librarian',
        11: 'marketing',
        12: 'none',
        13: 'other',
        14: 'programmer',
        15: 'retired',
        16: 'salesman',
        17: 'scientist',
        18: 'student',
        19: 'technician',
        20: 'writer'}


        age_group_show = show_movies_by_age_group(a, 20)

        age_predictions = recommend_movies_by_age_group(preds_age_group, a, items, user_movie_ratings_age_group, 20)

        occ_dict.get(int(form.occupation.data))

        occ_show = show_movies_by_occ(occ_dict.get(int(form.occupation.data)), 20)
        occ_predictions = recommend_movies_by_occupation(preds_occupation, int(form.occupation.data), items, 20)


        return render_template('show_new_user.html', age=form.age.data,
                               occupation=occ_dict.get(int(form.occupation.data)),
                               age_group_show=age_group_show.to_html(),
                               age_recommendation=age_predictions[['movie title', 'release date', 'rank']].to_html(),
                               occ_show=occ_show.to_html(),
                               occ_recommendation=occ_predictions[['movie title', 'release date', 'rank']].to_html()
                               # gender_recommendation=gender_predictions[['movie title', 'release date', 'rank']].to_html()
                               )
    else:
        if form.errors:
            flash(message=form.errors.values())

        return render_template('new.html', form=form)




if __name__ == '__main__':
    app.run()
