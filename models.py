from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# user module
class User(db.Model, UserMixin):

    # table name (overridden)
    __tablename__ = 'user'

    # columns of table
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    # relations between tables (user as parent table)
    customer_id = db.relationship('Customer', backref='user', lazy='dynamic')
    stock_id = db.relationship('Stock', backref='user', lazy='dynamic')
    cart_id = db.relationship('Cart', backref='user', lazy='dynamic')
    billing_id = db.relationship('Billing', backref='user', lazy='dynamic')

    def __init__(self, firstname, lastname, email, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password) # hashed the password

    # function to check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)





class Customer(db.Model):

    id = id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(64))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    cart_id = db.relationship('Cart', backref='customer', lazy='dynamic')

    def __init__(self, firstname, lastname, email, address, user_id):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.address = address
        self.user_id = user_id


# stock module
class Stock(db.Model):


    # columns of table
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=True)
    item_price = db.Column(db.Integer, nullable=True)
    item_qty = db.Column(db.Integer, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def __init__(self, item_name, item_price, item_qty, user_id):
        self.item_name = item_name
        self.item_price = item_price
        self.item_qty = item_qty
        self.user_id = user_id


class Cart(db.Model):


    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    item_name = db.Column(db.String(100))
    item_price = db.Column(db.Integer)
    item_quantity = db.Column(db.Integer)
    total_amount = db.Column(db.Integer)
    generated_at = db.Column(db.DateTime, default=datetime.now)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'))

    def __init__(self, customer_name, item_name, item_price, item_quantity, total_amount, user_id, customer_id):
        self.customer_name = customer_name
        self.item_name = item_name
        self.item_price = item_price
        self.item_quantity = item_quantity
        self.total_amount = total_amount
        self.user_id = user_id
        self.customer_id = customer_id


    # def final_amount(total_amount):

class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    total_amount = db.Column(db.Integer)
    generated_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def __init__(self, customer_name, total_amount, user_id):
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.user_id = user_id

