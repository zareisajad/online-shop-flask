from app import app, db 
from flask import render_template, flash, redirect, url_for, request
from app.models import Products
from base64 import b64encode
import base64


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic

@app.route('/')
def index():
    pics = Products.query.all()
    return render_template('index.html', pics=pics)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.getlist('file')
    for f in file:
        data = f.read()
        render_file = render_picture(data)
        newfile = Products(data=data, rendered_data=render_file)
        db.session.add(newfile)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/<int:id>')
def pic(id):
    get_pic = Products.query.filter_by(id=id).first()
    return render_template('pic.html', pic=get_pic)