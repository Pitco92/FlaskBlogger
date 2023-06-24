from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, NamerForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor
from dotenv.main import load_dotenv
import os

# load env
load_dotenv()

# Create a Flask instance
app = Flask(__name__)
ckeditor = CKEditor(app)

# add database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + os.environ['DB_USER'] + ":" + os.environ['DB_PASS'] + "@" + os.environ['DB_HOST'] + "/blogusers"

# secret key
app.config['SECRET_KEY'] = os.environ['APP_KEY']

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Manage Logins
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

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
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
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
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
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

# Add Post Page
@app.route('/add-post', methods=["GET", "POST"])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id = poster, slug=form.slug.data)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        #form.author.data = ""
        form.slug.data = ""

        #Add post data to database
        db.session.add(post)
        db.session.commit()

        #return a message
        flash("Post is submitted succesfully")

    #redirect to webpage
    return render_template("add_post.html", form=form)

# View post page
@app.route('/posts')
def posts():

    posts = Posts.query.order_by(desc(Posts.date_posted))
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        #post.author = form.author.data
        post.slug = form.slug.data

        #Update DB
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.content.data = post.content
        #form.author.data = post.author
        form.slug.data = post.slug
        return render_template('edit_post.html', form=form)
    else:
        flash("You are not allowed to edit this post")
        posts = Posts.query.order_by(desc(Posts.date_posted))
        return render_template("posts.html", posts=posts)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:   
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Post deleted, i hope you know what you did ...")

            posts = Posts.query.order_by(desc(Posts.date_posted))
            return render_template("posts.html", posts=posts)

        except:
            flash("Whoops, there was a problem with deleting your post. But you did your best and that is what count!")
            
            posts = Posts.query.order_by(desc(Posts.date_posted))
            return render_template("posts.html", posts=posts)
        
    else:
        flash("You are not allowed to delete this post")

        posts = Posts.query.order_by(desc(Posts.date_posted))
        return render_template("posts.html", posts=posts)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #chech pass hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - Do you try to hack?!")
        else:
            flash("User does not exist - Nice try buddy.")

    return render_template('login.html', form=form)

# Create logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You are logged out - Bye")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template("dashboard.html",
                                   form = form,
                                   name_to_update = name_to_update)
        except:
            flash("Error! Looks like there was a problem. Maybe try it again.")
            return render_template("dashboard.html",
                                   form = form,
                                   name_to_update = name_to_update)
    else:
        return render_template("dashboard.html",
                                   form = form,
                                   name_to_update = name_to_update,
                                   id = id)

# Search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from search bar
        post.searched = form.searched.data

        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html", 
                               form = form, 
                               searched = post.searched,
                               posts=posts)

# Create blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Couple user to post
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Posts", backref='poster')

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