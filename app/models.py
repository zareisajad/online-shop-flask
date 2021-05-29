from app import db


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    rendered_data = db.Column(db.Text)