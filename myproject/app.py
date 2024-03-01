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
from models import db, Accounts, Review, Product, Cart, ShippingInformation
from classes import AddProductForm
import stripe
from flask_mail import Mail, Message


app = Flask(__name__)

  # Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

  # Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '4d40fd7fcac258f0aa974b12a1422f10'

# Configure e-mail
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'oefenflaskminprog@gmail.com'
app.config["PASSWORD"] = 'MinProg1sept2024'
app.config["USE_SSL"] = True
mail = Mail(app)

#set stripe API
stripe.api_key = 'sk_test_51OmEnSFkF5U5bz8e2ODfcCQB0f6a02FAqQ5LofHcsCJ2KOT0am1NSUHLZjkZ5wHviSHwkqLWLJ0xtVl93EEMMNLy00jMmghGG2'

Session(app)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/homepage")
    else:
        return redirect("/login")


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

@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page after logging out
    return redirect("/login")

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

@app.route("/review", methods=["GET", "POST"])
def submit_review():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        
        stars = int(request.form.get("stars"))
        comment = request.form.get("comment")
        user_id = session["user_id"]
        
        review = Review(user_id=user_id, stars=stars, comment=comment)  # Create a Review object
        
        try:
            db.session.add(review)  # Add the Review object to the session
            db.session.commit()  # Commit the changes to the database
            return redirect("/review")
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of an error
            return f"Error: {str(e)}"
    else:
        reviews = db.session.query(Review, Accounts.username).join(Accounts, Review.user_id == Accounts.id).all()
        return render_template("review.html", reviews=reviews)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Check if the user is logged in as admin
    if "user_id" not in session:
        return redirect("/login")

    user = Accounts.query.get(session["user_id"])
    if user.username != "adminusername":  # Replace with your actual admin username
        return "you are not an admin"

    form = AddProductForm()

    if form.validate_on_submit():
        # Save the uploaded image
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Create a new product
        new_product = Product(name=form.name.data, price=form.price.data, image=filename)

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect("/admin")
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

    # Fetch all products from the database
    products = Product.query.all()

    return render_template("admin_panel.html", form=form, products=products)

# Modify homepage route to display products
@app.route("/homepage")
def homepage():
    products = Product.query.all()
    return render_template("homepage.html", products=products)

@app.route("/product/<int:id>")
def product_details(id):
    product = Product.query.get_or_404(id)
    return render_template("product.html", product=product)

@app.route("/checkout/<int:id>", methods=["POST"])
def create_checkout_session(id):
    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = int(sum(item.product.price * item.quantity for item in cart_items))  # Convert to integer

    session_id = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "your cart",
                    },
                    "unit_amount": total_price,
                },
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url=url_for("payment_success", _external=True),
        cancel_url=url_for("payment_cancelled", _external=True),
    ).id
    return redirect(url_for("checkout", session_id=session_id, user_id=id))


@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_id = db.session.query(Cart.id).filter_by(user_id=user_id).scalar()

    if cart_items:
        return render_template("checkout.html", cart_items=cart_items, total_price=total_price, cart_id=cart_id)
    else:
        flash("Your cart is empty.", "warning")
        return redirect("/homepage")

@app.route("/payment/cancelled")
def payment_cancelled():
    # Handle cancelled payment
    return "Payment cancelled."

@app.route("/add_to_cart/<int:id>", methods=["POST"])
def add_to_cart(id):
    if "user_id" not in session:
        flash("Please log in to add items to your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    product = Product.query.get_or_404(id)

    # Check if the item is already in the cart
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()

    # Update session with cart information
    session["cart"] = [{"product_id": item.product_id, "quantity": item.quantity} for item in Cart.query.filter_by(user_id=user_id)]

    flash(f"{product.name} added to cart.", "success")
    return redirect("/homepage")

@app.route("/remove_from_cart/<int:id>", methods=["POST"])
def remove_from_cart(id):
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    cart_item = Cart.query.get_or_404(id)
    if cart_item.quantity > 1:
        # Decrement the quantity if it's greater than 1
        cart_item.quantity -= 1
    else:
        # Remove the item from the cart if the quantity is 1
        db.session.delete(cart_item)

    db.session.commit()

    flash("Item removed from cart.", "success")
    return redirect("/cart")

@app.route("/delete_product/<int:id>", methods=["POST"])
def delete_product(id):
    if "user_id" not in session:
        flash("Please log in as admin to delete products.", "warning")
        return redirect("/login")

    user = Accounts.query.get(session["user_id"])
    if user.username != "adminusername":  # Replace with your actual admin username
        flash("You are not authorized to delete products.", "danger")
        return redirect("/admin")

    product = Product.query.get_or_404(id)

    # Fetch associated cart items for the product
    cart_items = Cart.query.filter_by(product_id=id).all()

    try:
        # Delete associated cart items
        for cart_item in cart_items:
            db.session.delete(cart_item)

        # Delete the product
        db.session.delete(product)
        db.session.commit()

        flash(f"Product {product.name} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect("/admin")


@app.route("/cart")
def view_cart():
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@app.route("/shipping_info", methods=["POST"])
def submit_shipping_info():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        
        user_id = session["user_id"]
        address = request.form.get("address")
        city = request.form.get("city")
        state_province = request.form.get("state_province")
        zipcode = request.form.get("zipcode")
        country = request.form.get("country")
        phone = request.form.get("phone")
        date_of_birth = request.form.get("date_of_birth")
        
        shipping_info = ShippingInformation(user_id=user_id, address=address, city=city, state_province=state_province, zipcode=zipcode, country=country, phone=phone, date_of_birth=date_of_birth)
        
        try:
            db.session.add(shipping_info)
            db.session.commit()
            return redirect("/success")  # Redirect to a success page after submitting shipping information
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
    else:
        return "Method not allowed"  # Only POST requests are allowed for submitting shipping information

def send_email(subject, body, recipients):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)

@app.route("/success")
def payment_success():
    # Fetch user's cart items and shipping information
    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    shipping_info = ShippingInformation.query.filter_by(user_id=user_id).first()

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Send email notification
    send_email("Your payment was successful", "Thank you for ordering", [shipping_info.email])

    return render_template("success.html", cart_items=cart_items, shipping_info=shipping_info, total_price=total_price)

