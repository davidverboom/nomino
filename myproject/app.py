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
from classes import AddProductForm, ShippingInformationForm
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

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"]
}

stripe.api_key = stripe_keys["secret_key"]
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
        new_product = Product(name=form.name.data, price=form.price.data, image=filename, description=form.description.data)

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

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://localhost:5000/"
    stripe.api_key = stripe_keys["secret_key"]
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = int(sum(item.product.price * item.quantity for item in cart_items))  # Convert to integer

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + f"success?session_id={{CHECKOUT_SESSION_ID}}&user_id={user_id}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "your cart",
                        },
                        "unit_amount": total_price,
                    },
                    "quantity": 100,
                },
            ],
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403
    

@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    shipping_info = ShippingInformation.query.filter_by(user_id=user_id).first()

    if cart_items:
        return render_template("checkout.html", cart_items=cart_items, total_price=total_price, shipping_info=shipping_info)
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

@app.route("/shipping_info", methods=["GET", "POST"])
def shipping_info():
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    form = ShippingInformationForm()
    if "user_id" not in session:
        return redirect("/login")

    if form.validate_on_submit():
        user_id = session["user_id"]
        shipping_info = ShippingInformation(
            user_id=user_id, 
            name=form.name.data, 
            email=form.email.data, 
            address=form.address.data, 
            city=form.city.data, 
            state_province=form.state_province.data, 
            zipcode=form.zipcode.data, 
            country=form.country.data, 
            phone=form.phone.data, 
        )
        
        try:
            db.session.add(shipping_info)
            db.session.commit()
            return redirect("/checkout")
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect("/shipping_info")

    if cart_items:
        return render_template("shipping_info.html", form=form, cart_items=cart_items, total_price=total_price)
    else:
        flash("Your cart is empty.", "warning")
        return redirect("/homepage")


@app.route("/success")
def payment_success():
    # Fetch user's cart items and shipping information
    user_id = request.args.get('user_id')
    if not user_id:
        return "User ID not found", 400
    user_id = int(user_id)
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    shipping_info = ShippingInformation.query.filter_by(user_id=user_id).first()

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render_template("success.html", cart_items=cart_items, shipping_info=shipping_info, total_price=total_price)

