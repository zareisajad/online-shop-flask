import base64
from app import app, db 
from flask import render_template, flash, redirect, url_for, request
from app.models import Products, Cart
from app.forms import AddProductForm


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic


@app.route('/')
def products():
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
                        sold = 0,data_gallery=data_gallery, rendered_gallery=rendered_g)
        db.session.add(product)
        db.session.commit()
        flash('Your product is live now!')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)


@app.route('/manage', methods=['POST','GET'])
def manage_products():
    products = Products.query.all()
    return render_template('manage_products.html', products=products)


@app.route('/del/<int:id>', methods=['GET', 'POST'])
def delete(id):
    del_product = Products.query.get(id)
    c = Cart.query.get(id)
    db.session.delete(del_product)
    db.session.commit()
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('manage_products'))


@app.route('/p/<int:id>',methods=['GET', 'POST'])
def product_detail(id):
    product = Products.query.filter_by(id=id).first()
    return render_template('product_detail.html', product=product)


@app.route('/cart/<int:id>', methods=['POST','GET'])
def cart(id):
    c = Cart.query.filter_by(id=id).first()
    if not c:
        p = Products.query.filter_by(id=id).first()
        cart = Cart(data=p.data, rendered_data=p.rendered_data,title=p.title,
                    price=p.price,discunted=p.discunted, number=1)
        db.session.add(cart)
        db.session.commit()
        flash('Added to your cart!')
        return redirect(url_for('products'))
    flash('This item is already in your cart!')
    return redirect(url_for('products'))


@app.route('/c/add/<int:id>', methods=['POST','GET'])
def add_num(id):
    n = Cart.query.filter_by(id=id).first()
    n.number += 1
    db.session.commit()
    return redirect(url_for('show_cart'))


@app.route('/c/reduce/<int:id>', methods=['POST','GET'])
def reduce_num(id):
    n = Cart.query.filter_by(id=id).first()
    n.number -= 1
    db.session.commit()
    return redirect(url_for('show_cart'))


@app.route('/cart', methods=['POST','GET'])
def show_cart():
    c = Cart.query.all()
    return render_template('cart.html', c=c)


@app.route('/del/cart/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    del_cart = Cart.query.get(id)
    db.session.delete(del_cart)
    db.session.commit()
    return redirect(url_for('show_cart'))