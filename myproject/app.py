import os

from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from models import db, Accounts
from models import db, Profile

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
            return "Apology4"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "Apology5"

        # Query database for username
        user = Accounts.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user.hash, request.form.get("password")):
            return "Apology6"

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
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate inputs
        if not username or not password or not confirmation:
            return "Apology1"
        elif password != confirmation:
            return "Apology2"

        # Check if username already exists
        existing_user = Accounts.query.filter_by(username=username).first()
        if existing_user:
            return "Apology3"

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user using the Accounts model
        new_user = Accounts(username=username, hash=hashed_password)

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

 
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    user_profile = Profile.query.filter_by(user_id=user_id).first()
    
    return render_template("profile.html", profile=user_profile)

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")
    
    # Retrieve the user's profile based on the user_id from the session
    user_id = session["user_id"]
    user_profile = Profile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        # Update the user's profile based on the form data
        full_name = request.form.get("full_name")
        date_of_birth = request.form.get("date_of_birth")
        education = request.form.get("education")
        institution = request.form.get("institution")

        if not user_profile:
            new_profile = Profile(user_id=user_id, full_name=full_name, date_of_birth=date_of_birth,
                                  education=education, institution=institution)
            try:
                db.session.add(new_profile)
                db.session.commit()
                return redirect("/profile")
            except Exception as e:
                db.session.rollback()
                return f"Error: {str(e)}"

        # Update the existing user's profile
        if user_profile:
            user_profile.full_name = full_name
            user_profile.date_of_birth = date_of_birth
            user_profile.education = education
            user_profile.institution = institution

            try:
                db.session.commit()
                return redirect("/profile")
            except Exception as e:
                db.session.rollback()
                return f"Error: {str(e)}"

        return redirect("/profile")

    return render_template("edit_profile.html", profile=user_profile)
