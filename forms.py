from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, RadioField, validators

from wtforms.validators import DataRequired, NumberRange

class ExistingUserForm(FlaskForm):
    userID = IntegerField('User ID', validators=[DataRequired(), NumberRange(1, 943)])

class NewUserForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(1, 100)])
    occupation = RadioField('Occupation', choices=[
        (0, 'administrator'),
 (1, 'artist'),
 (2, 'doctor'),
 (3, 'educator'),
 (4, 'engineer'),
 (5, 'entertainment'),
 (6, 'executive'),
 (7, 'healthcare'),
 (8, 'homemaker'),
 (9, 'lawyer'),
 (10, 'librarian'),
 (11, 'marketing'),
 (12, 'none'),
 (13, 'other'),
 (14, 'programmer'),
 (15, 'retired'),
 (16, 'salesman'),
 (17, 'scientist'),
 (18, 'student'),
 (19, 'technician'),
 (20, 'writer')], coerce=int)

    # gender = RadioField('Gender', choices=[(1, 'Male'), (0, 'Female')], coerce=int)

