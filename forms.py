from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, IntegerField, TextAreaField, SelectField, SelectMultipleField)
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=3, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20, message='Username must be min 4 to max 20 characters!')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=3, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()],  render_kw={'disabled':'disabled'})
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)], render_kw={'disabled':'disabled'})
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Update')



class AddCustomer(FlaskForm):
    firstname = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(message='Please enter valid email!'), Length(min=7, max=150)])
    address = TextAreaField('Address', validators=[Length(max=200)])
    submit = SubmitField('Submit')


class AddProduct(FlaskForm):
    item_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    item_price = IntegerField('Price', validators=[DataRequired()])
    item_qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')



class CreateBill(FlaskForm):
    customer = SelectField('Select Customer', choices=[])
    products = SelectField('Select Product', choices=[])
    item_qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add To Bill')



class InvoiceForm(FlaskForm):
    products = SelectField('Products', choices=[])
    item_qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add To Cart')