from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import UserMixin

from app import db, login, app


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    photo = db.Column(db.String(200))
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discounted = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    sold = db.Column(db.Integer)
    short_desc = db.Column(db.String)
    desc = db.Column(db.String)
    rate = db.Column(db.Integer)
    gallery = db.relationship('Gallery', backref='gallery', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='category')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    active = db.Column(
        'is_active', db.Boolean(), nullable=False, server_default='1')
    email_confirmed_at = db.Column(db.DateTime())
    cart = db.relationship('Cart', backref='cart')
    orders = db.relationship('Orders', backref='orders')
    roles = db.relationship('Role', secondary='user_roles')

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(
        db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(
        db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    product_id = db.Column(db.Integer)
    number = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    total = db.Column(db.Integer)
    cart_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orders_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String)
    payment_method = db.Column(db.String)
    name = db.Column(db.String)
    country = db.Column(db.String)
    city = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    total = db.Column(db.Integer)
    product_id = db.Column(db.String)
    number = db.Column(db.Integer)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '{}'.format(self.name)


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pics = db.Column(db.String(264))
    p_id = db.Column(db.Integer, db.ForeignKey('products.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
