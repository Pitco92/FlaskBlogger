from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from dotenv.main import load_dotenv
import os

# load env
load_dotenv()

# Create a Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['APP_KEY']

#create a form class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a route decorator
@app.route('/')
def index():
    first_name = "Peter"
    return render_template("index.html", 
                           first_name = first_name)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", 
                           user_name = name)

#Create custom error message

#Invalid URL

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#internal server Error

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted succesfully!")

    return render_template("name.html", 
                           name = name, 
                           form = form)
