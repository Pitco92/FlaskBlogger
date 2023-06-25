
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

# Create a login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a post form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
    about_author = TextAreaField("About author")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create a form class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create a form class password
class PasswordForm(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")