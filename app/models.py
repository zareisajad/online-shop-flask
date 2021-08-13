from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
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
    comments = db.relationship('Comments', backref='comments')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    cart = db.relationship('Cart', backref='cart')
    orders = db.relationship('Orders', backref='orders')
    role = db.Column(db.String())

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
    start_payment_date = db.Column(db.DateTime)
    create_order_date = db.Column(db.DateTime)
    finish_payment_date = db.Column(db.DateTime)
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


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = name = db.Column(db.String(50))
    email = db.Column(db.String)
    comment = db.Column(db.String(200))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    create_date = db.Column(db.DateTime)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
