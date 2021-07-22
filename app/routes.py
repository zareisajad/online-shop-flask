import os
import datetime 
from datetime import timedelta
import humanize
from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename
from app import app, db 
from app.models import Products, Cart, Gallery, Category, User, Orders
from app.forms import AddProductForm, AddCategoryForm, FilterProductsForm,\
                      RegisterationForm, LoginForm, CheckoutForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products'))
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data
            )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user - have fun')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products'))   
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('''We cant find a user with this
                    email please register first!''')
            return redirect(url_for('login'))
        elif user and not user.check_password(form.password.data):
            flash('password is wrong')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('products')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('products'))


@app.route('/')
def products():
    pic = Products.query.all()
    category = Category.query.all()
    if not pic:
        flash('There is no products yet. you can add from top menu')
    return render_template('products.html', pic=pic, category=category)


@app.route('/add-product', methods=['POST','GET'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        c = Category.query.filter_by(name=str(form.category.data)).first()
        uploaded_file = form.photo.data
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        url = (os.path.join('static/images',filename))
        p = Products(
            title=form.title.data, price=form.price.data,
            discounted=form.discounted.data, sold=0, rate=0, 
            inventory=form.inventory.data, photo=url, category_id=c.id)
        db.session.add(p)
        db.session.commit()
        images = form.photos.data
        for img in images:
            filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_GALLERY'],filename))
            url = (os.path.join('static/gallery', filename))
            files = Gallery(pics=url, p_id=p.id)
            db.session.add(files)
        db.session.commit()
        flash('Your product is live now!')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)


@app.route('/add-category', methods=['POST','GET'])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category added.')
        return redirect(url_for('add_product'))
    category = Category.query.all()
    return render_template(
        'add_category.html', form=form, category=category)


@app.route('/category/<int:id>', methods=['POST','GET'])
def category(id):
    pro = Products.query.filter_by(category_id=id).all()
    return render_template('products_category.html', pro=pro)


@app.route('/filter', methods=['POST','GET'])
def filter_products():
    form = FilterProductsForm()
    return render_template('filter.html', form=form)


@app.route('/f', methods=['POST','GET'])
def filter():
    form = FilterProductsForm()
    global keyword
    keyword = Products.query.filter(
        Products.title.contains(form.keyword.data),
        Products.category==form.category.data,
        Products.price>form.min_price.data,
        Products.price<form.max_price.data
        ).order_by(asc(Products.price)).all()
    return render_template('filter_resualt.html', keyword=keyword)


@app.route('/popular-filter', methods=['POST','GET'])
def popular():
    keyword.sort(key=lambda i: i.rate, reverse=True)
    return render_template(
        'filter_resualt.html', keyword=keyword)


@app.route('/sold-filter', methods=['POST','GET'])
def sold():
    keyword.sort(key=lambda i: i.sold, reverse=True)
    return render_template(
        'filter_resualt.html', keyword=keyword)


@app.route('/expensive_filter', methods=['POST','GET'])
def expensive():
    keyword.sort(key=lambda i: i.price, reverse=True)
    return render_template(
        'filter_resualt.html', keyword=keyword)


@app.route('/cheapest-filter', methods=['POST','GET'])
def cheapest():
    keyword.sort(key=lambda i: i.price)
    return render_template(
        'filter_resualt.html', keyword=keyword)


@app.route('/newst-filter', methods=['POST','GET'])
def newst():
    keyword.sort(key=lambda i: i.date, reverse=True)
    return render_template(
        'filter_resualt.html', keyword=keyword)


@app.route('/popular', methods=['POST','GET'])
def popular_filter():
    keyword = Products.query.order_by(desc(Products.rate)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/most-sold', methods=['POST','GET'])
def sold_filter():
    keyword = Products.query.order_by(desc(Products.sold)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/expensive', methods=['POST','GET'])
def expensive_filter():
    keyword = Products.query.order_by(desc(Products.price)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/cheapest', methods=['POST','GET'])
def cheapest_filter():
    keyword = Products.query.order_by(asc(Products.price)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/new', methods=['POST','GET'])
def newst_filter():
    keyword = Products.query.order_by(desc(Products.date)).all()
    return render_template('keyword.html', keyword=keyword)


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
    category = Category.query.filter_by(id=product.category_id).first()
    return render_template(
        'product_detail.html', product=product,
         gallery=gallery, category=category)


@app.route('/orders-list', methods=['POST','GET'])
def orders():
    o = Orders.query.all()
    u = User.query.filter(User.id==Orders.orders_id).all()
    c = Cart.query.filter(Cart.cart_id==Orders.orders_id).all()
    return render_template(
        'orders.html', orders=o, user=u, cart=c ,zip=zip)


@app.route('/order<int:id>', methods=['POST','GET'])
def order_line(id):
    u = User.query.filter(User.id==id).all()
    c = Cart.query.filter(Cart.cart_id==id).all()
    p =[Products.query.filter(Products.id==i.product_id).first() for i in c]
    return render_template(
        'order_line.html',user=u, cart=c, product=p ,zip=zip)


@app.route('/user-checkout', methods=['POST','GET'])
@login_required
def checkout():
    c = Cart.query.filter(Cart.cart_id==current_user.id).all()
    p =[Products.query.filter(Products.id==i.product_id).first() for i in c]
    form = CheckoutForm()
    '''
    TODO everytime we go in checkout page an order stores in db
           fix it. (check orders table if forgot)
    '''
    return render_template('checkout.html', c=c, p=p, form=form, zip=zip)


@app.route('/user-payment', methods=['POST','GET'])
@login_required
def payment():
    form = CheckoutForm()
    if form.payment.data == 'online':
        orders = Orders(status='در انتظار پرداخت', orders_id=current_user.id, payment_method='آنلاین')
        db.session.add(orders)
    else:
        orders = Orders(status='در انتظار پرداخت', orders_id=current_user.id, payment_method='نقدی')
        db.session.add(orders)
    db.session.commit()
    flash('سفارش با موفقیت ثبت شد')
    return redirect(url_for('products'))


@app.route('/cart/<int:id>', methods=['POST','GET'])
@login_required
def cart(id):
    ca = Cart.query.filter(Cart.product_id==id, Cart.cart_id==current_user.id).first()
    if ca:
        flash('This item is already in cart!')
    else:
        c = Cart(product_id=id, number=1, amount=0,
                 total=0, cart_id=current_user.id)
        db.session.add(c)
        flash('Added to cart!')
    db.session.commit()
    return redirect(url_for('products'))


@app.route('/user-<int:id>', methods=['POST','GET'])
def show_cart(id):
    # get all the items that matchs with current_user.id in Cart table 
    c = Cart.query.filter(Cart.cart_id==current_user.id).all()
    if not c:
        flash('Your cart is empty!')
    # get all the products
    p =[Products.query.filter(Products.id==i.product_id).first() for i in c]
    return render_template('cart.html', p=p, c=c, zip=zip)


@app.route('/del/cart/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    c = Cart.query.filter(Cart.cart_id==current_user.id, Cart.product_id==id).first()
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('show_cart', id=current_user.id))


@app.route('/fa', methods=['GET', 'POST'])
def final_amount():
    c = Cart.query.filter(Cart.cart_id==current_user.id).all()
    p = Products.query.filter(Products.id==Cart.product_id).all()
    total = []
    for a,i in zip(c, p):
        if not i.discounted:
            amount = a.number * i.price
        else:
            amount = a.number * i.discounted
        total.append(amount)
        total_amount = sum(total)
        a.amount = amount
        a.total = total_amount
        db.session.commit()
    return redirect(url_for('checkout'))


@app.route('/c/add/<int:id>', methods=['POST','GET'])
def add_num(id):
    c = Cart.query.filter(Cart.product_id==id, Cart.cart_id==current_user.id).first()
    p = Products.query.filter(Products.id==id).first()
    if  p.inventory == 0:
        flash('You picked up the last one - there is nothing left')
        return redirect(url_for('show_cart', id=current_user.id))
    else:
        c.date = datetime.datetime.now()
        c.number += 1
        p.inventory -= 1
        db.session.commit()
    return redirect(url_for('show_cart', id=current_user.id))


@app.route('/c/reduce/<int:id>', methods=['POST','GET'])
def reduce_num(id):
    c = Cart.query.filter(Cart.product_id==id, Cart.cart_id==current_user.id).first()
    p = Products.query.filter(Products.id==id).first()
    if c.number != 0:
        c.date = datetime.datetime.now()
        c.number -= 1
        p.inventory += 1
        db.session.commit()
    else:
        return redirect(url_for('show_cart',id=current_user.id))
    return redirect(url_for('show_cart',id=current_user.id))


@app.route('/like/<int:id>', methods=['POST','GET'])
def add_rate(id):
    p = Products.query.filter_by(id=id).first()
    p.rate += 1
    db.session.commit()
    return redirect(url_for('products'))


@app.route('/dislike/<int:id>', methods=['POST','GET'])
def reduce_rate(id):
    p = Products.query.filter_by(id=id).first()
    p.rate -= 1
    db.session.commit()
    return redirect(url_for('products'))