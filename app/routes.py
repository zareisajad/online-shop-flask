import base64
from app import app, db 
from flask import render_template, flash, redirect, url_for, request
from app.models import Products
from app.forms import AddProductForm


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic


@app.route('/')
def products():
    """
    Here we display all the products with thumbnail,
    title, price and add to cart button
    """
    pic = Products.query.all()
    return render_template('products.html', pic=pic)


@app.route('/add', methods=['POST','GET'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        f = form.photo.data 
        data = f.read()
        render_file = render_picture(data)
        g = form.photos.data # list
        for i in g:
            data_gallery = i.read()
            rendered_g = render_picture(data_gallery)
        product = Products(data=data, rendered_data=render_file,
                        title=form.title.data, price=form.price.data,
                        discunted=form.discunted.data, inventory=form.inventory.data,
                        data_gallery=data_gallery, rendered_gallery=rendered_g)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)


@app.route('/manage', methods=['POST','GET'])
def manage_products():
    products = Products.query.all()
    return render_template('manage_products.html', products=products)


@app.route('/del/<int:id>', methods=['GET', 'POST'])
def delete(id):
    del_pic = Products.query.get(id)
    db.session.delete(del_pic)
    db.session.commit()
    return redirect(url_for('manage_products'))


@app.route('/p/<int:id>',methods=['GET', 'POST'])
def product_detail(id):
    product = Products.query.filter_by(id=id).first()
    return render_template('product_detail.html', product=product)