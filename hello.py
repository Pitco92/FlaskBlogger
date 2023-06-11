from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv.main import load_dotenv
import os

# load env
load_dotenv()

# Create a Flask instance
app = Flask(__name__)

# old SQLite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# add database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + os.environ['DB_USER'] + ":" + os.environ['DB_PASS'] + "@" + os.environ['DB_HOST'] + "/blogusers"

# secret key
app.config['SECRET_KEY'] = os.environ['APP_KEY']

# Initialize the database
db = SQLAlchemy(app)

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
#create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

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

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()

    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User added successfully")

    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
                           form = form,
                           name = name,
                           our_users = our_users)

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
