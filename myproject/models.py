from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Accounts(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False) 
    hash = db.Column(db.String, nullable=False)
    profile = db.relationship('Profile', backref='account', uselist=False)

class Profile(db.Model):
    __tablename__ = "profile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.String, nullable=False)
    education = db.Column(db.String, nullable=False)
    institution = db.Column(db.String, nullable=False)
