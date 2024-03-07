from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'avif'], 'Images only!')])
    description = StringField('Description', validators=[DataRequired()])
    three_d_view = FileField('3D View File', validators=[FileAllowed(['gltf'], 'GLTF files only!')])

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