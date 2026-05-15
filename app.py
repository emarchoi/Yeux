import os
from flask import Flask, render_template, request, session, redirect, url_for, g
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'choi_pogi'

# Database Configuration - MySQL (MariaDB)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://amari_dev:choi@localhost/yeux_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session Configuration - Store sa MariaDB
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False

# Initializations
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

'''
 + - - - - - - - - - +
 |                   |
 |   TABLES/MODELS   |
 |                   |
 + - - - - - - - - - +
'''

# User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# Film Table
class Film(db.Model):
    __tablename__ = 'films'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    season = db.Column(db.Integer, nullable=True)
    episode = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    
# Book Table
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    page = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# For Log-In Required
@app.before_request
def logged_in():

    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(session["user_id"])

'''
 + - - - - - - - - - +
 |                   |
 |      ROUTES       |
 |                   |
 + - - - - - - - - - +
'''
# Welcome Page - Default Route
@app.route("/")
def index():
    return render_template("index.html")

'''
 + - - - - - - - - - +
 |  LOGIN/REGISTER   |
 + - - - - - - - - - +
'''

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():

    user_error = False
    pass_error = False
    error = False

    session.clear()

    if request.method == "POST":

        # Validate Login Form
        if not request.form.get("username"):
            user_error = True
            return render_template("login.html", user_error=user_error)

        elif not request.form.get("password"):
            pass_error = True
            return render_template("login.html", pass_error=pass_error)

        # Search database for username
        data = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not data or not check_password_hash(data.password_hash, request.form.get("password")):
            error = True
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = data.id

        # Redirect user to home page
        return redirect("/home")

    else:
        return render_template("login.html")
    
# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():

    user_error = False
    pass_error = False
    conf_error = False
    error = False

    session.clear()

    if request.method == "POST":

        # Validate Registeration Form
        if not request.form.get("username"):
            user_error = True
            return render_template("register.html", user_error=user_error)

        elif not request.form.get("password"):
            pass_error = True
            return render_template("register.html", pass_error=pass_error)

        elif request.form.get("password") != request.form.get("confirmation"):
            conf_error = True
            return render_template("register.html", conf_error=conf_error)

        # Check if Username already EXISTS
        data = User.query.filter_by(username=request.form.get("username")).first()

        if data is not None:
            error = True
            return render_template("register.html", error=error)

        # Else, Successful Register New User
        else:
            new_user = User(
                username = request.form.get("username"),
                password_hash = generate_password_hash(request.form.get("password"))
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect("/login")

    else:
        return render_template("register.html")
    
# Logout Route
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# Welcome and Start Page <- Logged In
@app.route("/home")
@login_required
def home():

    # Get the Username to Display on "Welcome to Yeux,"
    name = User.query.get(session["user_id"])

    # This passes whatever name is stored in db.execute to the {{name}} in home.html
    return render_template("home.html", name=name.username)

'''
 + - - - - - - - - - +
 |                   |
 |    MOVIE ROUTE    |
 |                   |
 + - - - - - - - - - +
'''

# Film List Route
@app.route("/film", methods=["GET", "POST"])
@login_required
def film():
    
    # Get all the movies from the database
    films = Film.query.filter_by(user_id=session["user_id"]).all()

    return render_template("film.html", films=films)

# Add Film Route
@app.route("/film_add", methods=["POST"])
@login_required
def film_add():
    
    # Fetch data from form and add to DB
    new_film = Film(
        user_id = session["user_id"],
        title = request.form.get("title"),
        type = request.form.get("type").upper(),
        season = request.form.get("season"),
        episode = request.form.get("episodes"),
        status = request.form.get("status")
    )
    
    db.session.add(new_film)
    db.session.commit()

    return redirect("/film")

# Edit Film List
@app.route("/edit_film", methods=["POST"])
@login_required
def film_edit():

    title = request.form.get("title")
    seasons = request.form.get("season")
    episodes = request.form.get("episodes")
    status = request.form.get("status")

    if title:
        if not seasons or not episodes:
            Film.query.filter_by(user_id=session["user_id"], title=title).update({"status": status})
            db.session.commit()
        else:
            Film.query.filter_by(user_id=session["user_id"], title=title).update({"season": seasons, "episode": episodes, "status": status})
            db.session.commit()
            
    return redirect("/film")

# Remove Film List
@app.route("/delete_film", methods=["POST"])
@login_required
def film_delete():

    title = request.form.get("title")
    
    Film.query.filter_by(user_id=session["user_id"], title=title).delete()
    db.session.commit()

    return redirect("/film")

# Film List Filter
@app.route("/filter_film", methods=["POST"])
@login_required
def filter_film():

    filter = request.form.get("status")

    if filter == "alphabetical":
        films = Film.query.filter_by(user_id=session["user_id"]).order_by(Film.title.asc()).all()
        
    elif filter == "status":
        films = Film.query.filter_by(user_id=session["user_id"]).order_by(Film.status.desc()).all()

    elif filter == "type":
         films = Film.query.filter_by(user_id=session["user_id"]).order_by(Film.type.asc()).all()

    else:
        films = Film.query.filter_by(user_id=session["user_id"]).all()

    return render_template("film.html", films=films)

'''
 + - - - - - - - - - +
 |                   |
 |    BOOKS ROUTE    |
 |                   |
 + - - - - - - - - - +
'''

# Book List Route
@app.route("/book", methods=["GET", "POST"])
@login_required
def book():

    # Get all the books from the database
    books = Book.query.filter_by(user_id=session["user_id"]).all()
    
    return render_template("book.html", books=books)

# Add Book List
@app.route("/add_book", methods=["POST"])
@login_required
def add_book():

    # Fetch data from form and add to DB
    new_book = Book(
        user_id = session["user_id"],
        title = request.form.get("title"),
        type = request.form.get("type").upper(),
        page = request.form.get("pages"),
        status = request.form.get("status")
    )
    
    db.session.add(new_book)
    db.session.commit()

    return redirect("/book")

# Edit Book List
@app.route("/edit_book", methods=["POST"])
@login_required
def edit_book():

    title = request.form.get("title")
    pages = request.form.get("pages")
    status = request.form.get("status")
    
    Book.query.filter_by(user_id=session["user_id"], title=title).update({"page" : pages, "status": status})
    db.session.commit()

    return redirect("/book")

# Remove Book List
@app.route("/delete_book", methods=["POST"])
@login_required
def book_delete():

    title = request.form.get("title")

    Book.query.filter_by(user_id=session["user_id"], title=title).delete()
    db.session.commit()

    return redirect("/book")

# Film List Filter
@app.route("/filter_book", methods=["POST"])
@login_required
def filter_book():

    filter = request.form.get("status")

    if filter == "alphabetical":
        books = Book.query.filter_by(user_id=session["user_id"]).order_by(Book.title.asc()).all()

    elif filter == "status":
        books = Book.query.filter_by(user_id=session["user_id"]).order_by(Book.status.asc()).all()

    elif filter == "type":
        books = Book.query.filter_by(user_id=session["user_id"]).order_by(Book.type.asc()).all()
    else:
        books = Book.query.filter_by(user_id=session["user_id"]).all()

    return render_template("book.html", books=books)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function