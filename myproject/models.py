from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Accounts(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False) 
    email = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=False)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String, nullable=False)