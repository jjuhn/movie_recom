# Movie recommendation using movielens data set and SVD. 
Repository for Movie Recommendation system part of UIUC CS420 Final Project 

# Installation
This program runs on python 2.7X and uses Flask, Pandas, numpy and scipy.  
You could clone this project(download) and perform below commands in the command line.
- pip install flask
- pip install pandas
- pip install numpy 
- pip install scipy 
- pip install flask_wtf(This has been left out in the presentation video. Please install this as well.)

# Overview of Functions
- tools.py
    - get_all_predicted_ratings(ratings, k)
        - heart and soul of this recommendation system.  
        - ratings refers to pivoted dataframe that has one predictor(user_id, age or occupations) joined with 
        rating of items to be evaluated.  This function can be used not only in the movies but also in many different areas.
    - recommend_movies, recommend_movies_by_age_group, recommend_movies_by_occupation
        - uses the predictions from get_all_predicted_ratings function and returns the shorted, 
        more informative and sorted dataframe.  This function is for post processing of results
    - show_movies_by_age_group, show_movies_by_occ
        - display the mean rating sorted dataframe that is filtered using age_group or occupation.  
        The results are unnormalized hence 5 rated movie that has been rated once will always appear on top.  
        This is implemented to show the user the differences
- movie_rec.py
    - index()
        - directs to /index in the web. 
        - front page that shows the three menues. 
        - uses jinja2 templates
    - movies()
        - directs to /movies in the web. 
        - shows the list of all the movies and their average ratings in this dataset
        - also uses jinja2 templates
    - existingUser
        - directs to /existing
        - uses forms.py's ExistingUserForm. 
        - once validation is done, displays two tables, one for user already rated movies and one for recommendations
    - newUser
        - directs to /new_user
        - uses forms.py's NewUserForm 
        - once validation is done, displays two tables for each category.  One for mean average rating and one for recommendations for each category. 
- forms.py
    - ExistingUserForm
        - Flask way of implementing forms
    - NewUserForm
        - Flask way of implementing forms
# Implementation
- I am not 100% sure on the implementation part. I will regard this as deployment details
- Since this is a web application, you should first specify hosted options.  Here are some options
    - heroku
    - OpenShift
    - GAE
    - AWS 
    - Azure
    - PythonAnywhere
    - Self-host using WSGI(apache preferred for more security)
    
- virtualenv?
    - I prefer setting up python 2.7X environment using virtualenv first then using this virtualenv install above packages and run it. 
```commandline
pip install virtualenv 
python2.7X -m virtualenv some_env_name
```
- localhost:5000?
    - This uses port 5000. so please free up this port. 
    - This is the default when you run 
```commandline
virtualPython /path/to/this/directory/movie_recom/movie_rec.py
```
- download all the file and from movie_recom.tools import something?
- 


# Usage
- I will 
```commandline
pip install pandas
pip install numpy 
pip install scipy 
pip install flask_wtf
```

```python
from tools import get_all_predicted_ratings

ratings = some_rating_table.pivot(index='Predictor', columns='things_to_be_predicted', values='some_sort_of_ratings').fillna(0)
results_for_all_predictor = get_all_predicted_ratings(ratings, k=len(ratings)-1)

```

he 20% for the documentation submission includes 
5% for overview of functions, 
10% for implementation documentation, 
5% for usage documentation. 