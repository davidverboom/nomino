from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField, SubmitField
from wtforms.validators import DataRequired

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    image = FileField('Product Image', validators=[DataRequired()])
    submit = SubmitField('Add Product')

import secrets

secret_key = secrets.token_hex(16)
print(secret_key)