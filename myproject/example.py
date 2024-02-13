import os
import requests
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
from sqlalchemy import or_

from models import *

app = Flask(__name__)

  # Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

  # Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
    
        
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        # title = request.form.get("title")
        # author = request.form.get("author")
        # isbn = request.form.get("isbn")
        search = request.form.get("search")
        books = Book.query.filter(or_(Book.title == search, Book.author == search, Book.isbn == search))
        print("test2")
        print(book)
        if not books:
            return render_template("error.html", error = "No book with that criteria")
        else:
            return render_template("isbn.html", books = books)



@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    if request.method == "GET":
        book = Book.query.filter_by(isbn = isbn).first()
        reviews = Review.query.filter_by(book_id = isbn)
        print(f"{book.isbn}")
        response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{book.isbn}&jscmd=details&format=json")
        data = response.json()
        if "description" in data.get("details", {}):
            description = data["details"]["description"]
        else:
            description = "Description not available"
    
        print("test4")
        print(data)
        print(description)
        if book == None:
            return render_template("error.html",error = "Book does not exist in database")
        
        return render_template("book.html",book = book, reviews = reviews)
    
    elif request.method == "POST":
        book = Book.query.filter_by(isbn = isbn).first()
        reviews = Review.query.filter_by(book_id = isbn)
        rating = request.form.get("rate")
        user_id = session["user_id"]
        review_text = request.form.get("review_text")

        # test if user has already reviewed certain book
        if Review.query.filter_by(user_id = user_id, book_id = isbn).first() == None:
            print("Not reviewed")
            new_review = Review(user_id = user_id,book_id = isbn,rating = rating, text = review_text)
            db.session.add(new_review)
            db.session.commit()
            return render_template("book.html",book = book, reviews = reviews)
        else:
            return render_template("error.html", error = "You have already reviewed this book.")

    
# @app.route("/book/<isbn>/review",methods=["POST"])
# def review(isbn):

@app.route("/reviewed", methods = ["GET"])
def reviewed():
    user_id = session["user_id"]
    reviewed = Review.query.filter_by(user_id = user_id)

    return render_template("reviewed.html", reviewed = reviewed)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmed_password = request.form.get("confirmation")
        if User.query.filter_by(username=username).first():
            return apology("This username already exists",400)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        elif not password:
            return apology("must provide password", 400)
                # Ensure password was submitted
        elif not confirmed_password:
            return apology("must provide confirmation")
        
        elif password != confirmed_password:
            return apology("Passwords do not match", 400)
            # ensures confirmation password is equal to password
        
        
        else:
            hashed_password = generate_password_hash(password)
            # generats hashes password for security
            new_user = User(username = username, hash = hashed_password)

            # Adds users input to register
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            # login user

            return redirect("/")
    else:
        render_template("register.html") 


    return render_template("register.html")
            





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")