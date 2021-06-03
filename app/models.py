from app import db


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200))
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discounted = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    sold = db.Column(db.Integer)
    gallery = db.relationship('Gallery', backref='gallery', lazy='dynamic')


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pics = db.Column(db.String(264))
    p_id = db.Column(db.Integer, db.ForeignKey('products.id'))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200))
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discounted = db.Column(db.Integer)
    number = db.Column(db.Integer)