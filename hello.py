from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
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
migrate = Migrate(app, db)

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
#create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
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
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
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

# Create pw test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()


    # Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # clear the form
        form.email.data = ''
        form.password_hash.data = ''

        #look up user by email
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hash password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html", 
                           email = email, 
                           password = password,
                           pw_to_check = pw_to_check,
                           passed = passed, 
                           form = form)

# Upodate DB record
@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update)
        except:
            flash("Error! Looks like there was a problem. Maybe try it again.")
            return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update)
    else:
        return render_template("update.html",
                                   form = form,
                                   name_to_update = name_to_update,
                                   id = id)
    
@app.route("/delete/<int:id>", methods =['GET', 'POST'])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")

        our_users = Users.query.order_by(Users.date_added)

        return render_template("add_user.html",
                               form = form,
                               name = name,
                               our_users = our_users)

    except:
        flash("There was a problem. Maybe it works if you try again.")
        return render_template("add_user.html",
                               form = form,
                               name = name,
                               our_users = our_users)