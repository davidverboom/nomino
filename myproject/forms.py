from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import Accounts

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Accounts.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'avif'], 'Images only!')])
    description = StringField('Description', validators=[DataRequired()])

class ShippingInformationForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state_province = StringField('State/Province', validators=[DataRequired()])
    zipcode = StringField('Zip Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')