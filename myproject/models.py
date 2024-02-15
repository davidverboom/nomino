from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

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
    user = db.Column(db.String, primary_key=True, autoincrement=True)
    review_user = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=False)
