from flask import Flask
from flask import render_template, url_for, redirect, flash
from forms import ExistingUserForm, NewUserForm
from tools import *
from importing_tools import read_files

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my big secret'

users, ratings, items = read_files()


@app.route('/')
@app.route('/index')
def index():
    '''

    :return: index.html template
    '''
    return render_template('index.html')

@app.route('/movies')
def movies():
    '''

    :return: movies.html template with all the movies that are mean rated and sorted
    '''
    return render_template('movies.html', items=movie_ratings_sorted.to_html())

@app.route('/existing', methods=['GET', 'POST'])
def existingUser():
    '''

    :return: when form is filled returns show_user.html else existing.html.  show_user contains two tables.
    One with movies that the user rated and the other is for the recommendation.
    '''
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
