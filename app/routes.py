import os
from app import app, db 
from flask import render_template, flash, redirect, url_for
from app.models import Products, Cart, Gallery
from app.forms import AddProductForm
from werkzeug.utils import secure_filename


@app.route('/')
def products():
    pic = Products.query.all()
    if not pic:
        flash('There is no products yet. you can add from top menu')
    return render_template('products.html', pic=pic)


@app.route('/add', methods=['POST','GET'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        uploaded_file = form.photo.data
        filename = secure_filename(uploaded_file.filename)
        #file_ext = os.path.splitext(filename)[1]
        #if file_ext not in app.config['UPLOAD_EXTENSIONS']:
          #  flash('Only images allowed. [jpg , png ]')
          #  return redirect(url_for('products'))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        url = (os.path.join('static/images',filename))
        p = Products(title=form.title.data, price=form.price.data,
                    discounted=form.discounted.data, sold = 0,
                    inventory=form.inventory.data, photo=url)
        db.session.add(p)
        db.session.commit()
        # gallery
        images = form.photos.data
        for img in images:
            filename = secure_filename(img.filename)
           # file_ext = os.path.splitext(filename)[1]
          #  if file_ext not in app.config['UPLOAD_EXTENSIONS']:
             #   flash('Only images allowed. [jpg , png ]')
             #   return redirect(url_for('products'))
            img.save(os.path.join(app.config['UPLOAD_GALLERY'],filename))
            url = (os.path.join('static/gallery', filename))
            files = Gallery(pics=url, p_id=p.id)
            db.session.add(files)
        db.session.commit()
        flash('Your product is live now!')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)


@app.route('/manage', methods=['POST','GET'])
def manage_products():
    products = Products.query.all()
    if not products:
        flash('There is no products yet. you can add from top menu')
    return render_template('manage_products.html', products=products)


@app.route('/del/<int:id>', methods=['GET', 'POST'])
def delete(id):
    g = Gallery.query.all()
    for i in g:
        if i.p_id == id:
            name = i.pics.split('/')[2]
            db.session.delete(i)
            os.remove(app.config['UPLOAD_GALLERY']+'/'+name)

    del_product = Products.query.get(id)
    db.session.delete(del_product)
    db.session.commit()

    name = del_product.photo.split('/')[2]
    os.remove(app.config['UPLOAD_PATH']+'/'+name)

    c = Cart.query.get(id)
    if c:
        db.session.delete(c)
        db.session.commit()
    
    return redirect(url_for('manage_products'))


@app.route('/<int:id>',methods=['GET', 'POST'])
def product_detail(id):
    product = Products.query.filter_by(id=id).first()
    gallery = Gallery.query.all()
    return render_template(
        'product_detail.html', product=product, gallery=gallery)


@app.route('/cart/<int:id>', methods=['POST','GET'])
def cart(id):
    c = Cart.query.filter_by(id=id).first()
    if not c:
        p = Products.query.filter_by(id=id).first()
        cart = Cart(
            photo=p.photo, title=p.title,number=1,
            price=p.price, discounted=p.discounted)
        db.session.add(cart)
        db.session.commit()
        flash('Added to your cart!')
        return redirect(url_for('products'))
    else: 
        flash('This item is already in your cart!')
        return redirect(url_for('products'))
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
    if not c:
        flash('Your cart is empty!')
    return render_template('cart.html', c=c)


@app.route('/del/cart/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    del_cart = Cart.query.get(id)
    db.session.delete(del_cart)
    db.session.commit()
    return redirect(url_for('show_cart'))