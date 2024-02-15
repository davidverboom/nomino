import os
import re

from flask import current_app as app
from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from models import db, Accounts, Review

app = Flask(__name__)

  # Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files

  # Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/homepage")
    else:
        return redirect("/login")
    
@app.route("/homepage")
def homepage():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("homepage.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return "no username submitted"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "no password submitted"

        # Query database for username
        user = Accounts.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user.hash, request.form.get("password")):
            return "password does not match username"

        # Remember which user has logged in
        session["user_id"] = user.id

        # Check if the user is the admin
        if user.username == "admin_name":  # Replace with the actual admin username
            return redirect("/admin")

        # Redirect user to home page
        return redirect("/homepage")
    
    # Add a general return statement for GET requests
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Extract user input from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        profile_picture = request.files.get("profile_picture")  # Get the profile picture file

        # Validate inputs
        if not username or not email or not password or not confirmation:
            return "invalid input"
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return "invalid email format"
        elif password != confirmation:
            return "not the same password"

        # Check if username already exists
        existing_user = Accounts.query.filter_by(username=username).first()
        if existing_user:
            return "username already in database"

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save the profile picture
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            profile_picture_path = None

        # Create a new user using the Accounts model
        new_user = Accounts(username=username, email=email, hash=hashed_password, profile_picture=profile_picture_path)

        # Attempt to add the new user to the database and handle exceptions
        try:
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            return redirect("/login")
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
        
    else:
        return render_template("register.html")

@app.route("/review", methods=["GET","POST"])
def submit_review():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        
        stars = int(request.form.get("stars"))
        comment = request.form.get("comment")
        user_id = session["user_id"]
        
        new_review = Review(user_id=user_id, stars=stars, comment=comment)
        reviews = 
        
        try:
            db.session.add(new_review)
            db.session.commit()
            return redirect("/homepage")
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
    else:
        reviews = Review.query.all()  # Assuming you're fetching all reviews from the database
        return render_template("review.html", reviews=reviews)
