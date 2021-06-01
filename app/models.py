from app import db


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    rendered_data = db.Column(db.Text)
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discunted = db.Column(db.Integer) # TODO currect 'discounted' :|
    inventory = db.Column(db.Integer)
    sold = db.Column(db.Integer)
    data_gallery = db.Column(db.LargeBinary)
    rendered_gallery = db.Column(db.Text)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    rendered_data = db.Column(db.Text)
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    discunted = db.Column(db.Integer)
    number = db.Column(db.Integer)
