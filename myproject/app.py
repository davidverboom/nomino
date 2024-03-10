# Import Libraries
import os
import stripe
from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

# Import models and forms
from models import db, Accounts, Review, Product, Cart, ShippingInformation
from forms import AddProductForm, ShippingInformationForm, RegistrationForm

app = Flask(__name__)

"""
Set all configurations to make it even possible to run the app
"""

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
app.config["MAIL_DEFAULT_SENDER"] = 'oefenflaskminprog@gmail.com'
app.config["MAIL_PASSWORD"] = 'opda qkvv xebz lldi'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"]
}

stripe.api_key = stripe_keys["secret_key"]
Session(app)

"""
app features based on accounts and usersettings
"""


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

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return flash("no username submitted")
        elif not request.form.get("password"):
            return flash("no password submitted")

        user = Accounts.query.filter_by(
            username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(
            user.hash, request.form.get("password")):
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
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        profile_picture_path = None
        if form.profile_picture.data:
            # Save and give path to profile picture
            profile_picture_filename = secure_filename(
                form.profile_picture.data.filename)
            form.profile_picture.data.save(os.path.join(
                app.config['UPLOAD_FOLDER'], profile_picture_filename))
            profile_picture_path = os.path.join(
                app.config['UPLOAD_FOLDER'], profile_picture_filename)

        new_user = Accounts(username=form.username.data,
                            email=form.email.data, hash=hashed_password,
                            profile_picture=profile_picture_path)
        db.session.add(new_user)
        db.session.commit()
        # Log the user in and redirect to the login page or dashboard
        return redirect(url_for('login'))
    return render_template("register.html", form=form)


"""
app features to support the review function
"""


@app.route("/review", methods=["GET", "POST"])
def submit_review():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")

        # Small review form
        stars = int(request.form.get("stars"))
        comment = request.form.get("comment")
        user_id = session["user_id"]

        review = Review(user_id=user_id, stars=stars, comment=comment)

        try:
            db.session.add(review)
            db.session.commit()
            return redirect("/review")
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
    else:
        reviews = db.session.query(Review, Accounts.username).join(
            Accounts, Review.user_id == Accounts.id).all()
        return render_template("review.html", reviews=reviews)


"""
app features specific to the admin
"""


@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Check if the user is logged in as admin
    if "user_id" not in session:
        return redirect("/login")

    user = Accounts.query.get(session["user_id"])
    if user.username != "adminusername":
        return "you are not an admin"

    form = AddProductForm()

    if form.validate_on_submit():
        # Save the uploaded image
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Create a new product
        new_product = Product(name=form.name.data,
                              price=form.price.data,
                              image=filename,
                              description=form.description.data)

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect("/admin")
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

    products = Product.query.all()

    return render_template("admin_panel.html", form=form, products=products)


@app.route("/delete_product/<int:id>", methods=["POST"])
def delete_product(id):
    if "user_id" not in session:
        flash("Please log in as admin to delete products.", "warning")
        return redirect("/login")

    user = Accounts.query.get(session["user_id"])
    if user.username != "adminusername":
        flash("You are not authorized to delete products.", "danger")
        return redirect("/homepage")

    product = Product.query.get_or_404(id)
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


"""
all features to view the site
"""


@app.route("/homepage")
def homepage():
    products = Product.query.all()
    return render_template("homepage.html", products=products)


@app.route("/product/<int:id>")
def product_details(id):
    product = Product.query.get_or_404(id)
    return render_template("product.html", product=product)


"""
all functions involving the shopping cart
"""


@app.route("/cart")
def view_cart():
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity
                      for item in cart_items)

    return render_template("cart.html", cart_items=cart_items,
                           total_price=total_price)


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
    session["cart"] = [{"product_id": item.product_id, "quantity": item.quantity}
                       for item in Cart.query.filter_by(user_id=user_id)]

    flash(f"{product.name} added to cart.", "success")
    return redirect("/homepage")


@app.route("/remove_from_cart/<int:id>", methods=["POST"])
def remove_from_cart(id):
    if "user_id" not in session:
        flash("Please log in to access your cart.", "warning")
        return redirect("/login")

    cart_item = Cart.query.get_or_404(id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        # Remove the item from the cart if the quantity is 1
        db.session.delete(cart_item)

    db.session.commit()

    flash("Item removed from cart.", "success")
    return redirect("/cart")


"""
all functions for the payment API
"""


@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@app.route("/create-checkout-session")
# Deels overgenomen van Michael Herman van testdriven.io
def create_checkout_session():
    domain_url = "http://localhost:5000/"
    stripe.api_key = stripe_keys["secret_key"]
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = int(sum(item.product.price * item.quantity
                          for item in cart_items))

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


"""
Every feature for the checkout templates
"""


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
        return render_template("shipping_info.html", form=form, cart_items=cart_items,
                                total_price=total_price)
    else:
        flash("Your cart is empty.", "warning")
        return redirect("/homepage")


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
        return render_template("checkout.html", cart_items=cart_items,
                               total_price=total_price, shipping_info=shipping_info)
    else:
        flash("Your cart is empty.", "warning")
        return redirect("/homepage")


@app.route("/payment/cancelled")
def payment_cancelled():
    return render_template("cancelled.html")


"""
All necessities for a good success feature
"""


def send_email(subject, body, recipients):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)


@app.route("/success")
def payment_success():
    user_id = request.args.get('user_id')
    if not user_id:
        return "User ID not found", 400
    user_id = int(user_id)
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    shipping_info = ShippingInformation.query.filter_by(user_id=user_id).first()

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Send email notification
    send_email("Your payment was successful", "Thank you for ordering",
               [shipping_info.email])

    return render_template("success.html", cart_items=cart_items,
                           shipping_info=shipping_info, total_price=total_price)
