from app import db


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200))
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discounted = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    sold = db.Column(db.Integer)
    rate = db.Column(db.Integer)
    gallery = db.relationship('Gallery', backref='gallery', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='category')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    
    def __repr__(self):
        return '{}'.format(self.name)


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pics = db.Column(db.String(264))
    p_id = db.Column(db.Integer, db.ForeignKey('products.id'))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200))
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    discounted = db.Column(db.Integer)
    number = db.Column(db.Integer)