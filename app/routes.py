import os
import ast
import datetime
from functools import wraps

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse

from app import app, db
from app.models import Products, Cart, Gallery, Category, User, Orders
from app.forms import AddProductForm, AddCategoryForm, FilterProductsForm,\
                      RegisterationForm, LoginForm, CheckoutForm


def login_required_role(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
              return login.unauthorized()
            if ((current_user.role != role) and (role != "ANY")):
                return login.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# executes before any tasks
@app.before_first_request
def create_admin():
    """
    Create Admin User
    -----------------
    first before app executes any task
    we create a user and pass 'Admin' to User.role.
    """
    if not User.query.filter_by(email='admin@example.com').first():
        user = User(name='admin', email='admin@example.com', role='Admin')
        user.set_password('Password1')
        db.session.add(user)
        db.session.commit()


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register User
    -------------
    first if user is already registered, we redirect them to main page
    after extract name and email given from the user, and saving in database
    the hash of the password entered by user will store in db too.
    set_password defined in forms.py
    """
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('ثبت نام انجام شد')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login User
    ----------
    first if user is already logged in, we redirect them to main page
    after extract email and password from login form;
    we check if the email is in db or not, otherwise app flashs a message
    also we compare the given password with decoded hash that is in database.
    check_password defined in forms.py
    """
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('کاربری با ایمیل پیدا نشد')
            return redirect(url_for('login'))
        if user and not user.check_password(form.password.data):
            flash('رمز عبور اشتباه است')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_page')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/')
def main_page():
    """
    Main Page | products
    --------------------
    this page contains all the products cards.
    if there is no products then we flash a message.
    """
    all_products = Products.query.all()
    if not all_products:
        flash('محصولی موجود نیست')
    return render_template('main_page.html', all_products=all_products)


@app.route('/add-product', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def add_product():
    """
    Add New Product | *Avaiable For Admin*
    ---------------
    """
    form = AddProductForm()
    if form.validate_on_submit():
        c = Category.query.filter_by(name=str(form.category.data)).first()
        uploaded_file = form.photo.data
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        url = (os.path.join('static/images', filename))
        p = Products(
            title=form.title.data, price=form.price.data,
            discounted=form.discounted.data, sold=0, rate=0,
            short_desc=form.short_desc.data, desc=form.desc.data,
            inventory=form.inventory.data, photo=url, category_id=c.id)
        db.session.add(p)
        db.session.commit()
        images = form.photos.data
        for img in images:
            filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_GALLERY'], filename))
            url = (os.path.join('static/gallery', filename))
            files = Gallery(pics=url, p_id=p.id)
            db.session.add(files)
        db.session.commit()
        return redirect(url_for('main_page'))
    return render_template('add_product.html', form=form)


@app.route('/add-category', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def add_category():
    """
    Add New Category | *Avaiable For Admin*
    ----------------
    """
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('دسته بندی جدید ایجاد شد')
        return redirect(url_for('add_product'))
    category = Category.query.all()
    return render_template(
        'add_category.html', form=form, category=category)


@app.route('/manage', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def manage_products():
    """
    Manage Products Page | *Avaiable For Admin*
    --------------------
    """
    all_products = Products.query.all()
    if not all_products:
        flash('محصولی موجود نیست')
    return render_template('manage_products.html', products=all_products)


@app.route('/del/<int:id>', methods=['GET', 'POST'])
@login_required_role(role="Admin")
def delete(id):
    """
    Delete Products | *Avaiable For Admin*
    ---------------
    """
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


@app.route('/<int:id>', methods=['GET', 'POST'])
def product_detail(id):
    """
    Products Details
    ---------------
    """
    product = Products.query.filter_by(id=id).first()
    gallery = Gallery.query.all()
    category = Category.query.filter_by(id=product.category_id).first()
    return render_template(
        'product_detail.html', product=product,
         gallery=gallery, category=category)


@app.route('/cart/<int:id>', methods=['POST','GET'])
@login_required
def cart(id):
    """
    Add Products To Cart
    --------------------
    """
    ca = Cart.query.filter(
         Cart.product_id==id, Cart.cart_id==current_user.id).first()
    if ca:
        flash('این محصول قبلا اضافه شده است')
    else:
        c = Cart(product_id=id, number=1, amount=0,
                 total=0, cart_id=current_user.id)
        db.session.add(c)
        p = Products.query.filter(Products.id==id).first()
        p.sold += 1
        p.inventory -= 1
        flash('به سبد خرید اضافه شد')
    db.session.commit()
    return redirect(url_for('main_page'))


@app.route('/user-<int:id>', methods=['POST','GET'])
@login_required
def show_cart(id):
    """
    User Cart
    ---------
    """
    user_cart = current_user.cart
    if not user_cart:
        flash('سبد خرید شما خالی است')
    cart_products =[
        Products.query.filter(Products.id==i.product_id).first()
        for i in current_user.cart
    ]
    return render_template(
        'cart.html',cart_products=cart_products, user_cart=user_cart, zip=zip)


@app.route('/del/cart/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    """
    Remove Items From Cart
    ----------------------
    """
    c = Cart.query.filter(Cart.cart_id==current_user.id,
                          Cart.product_id==id).first()
    p = Products.query.filter(Products.id==id).first()
    p.sold -= c.number
    p.inventory += c.number
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('show_cart', id=current_user.id))


@app.route('/c/add/<int:id>', methods=['POST','GET'])
def add_num(id):
    """
    Add Product Number In Cart
    --------------------------
    """
    c = Cart.query.filter(Cart.product_id==id,
                          Cart.cart_id==current_user.id).first()
    p = Products.query.filter(Products.id==id).first()
    while c.number < p.inventory:
        c.number += 1
        db.session.commit()
        return redirect(url_for('show_cart', id=current_user.id))
    else:
        flash('بیشتر از این تعداد موجود نیست')
        return redirect(url_for('show_cart', id=current_user.id))


@app.route('/c/reduce/<int:id>', methods=['POST','GET'])
def reduce_num(id):
    """
    Reduce Product Number In Cart
    ---------------
    """
    c = Cart.query.filter(Cart.product_id==id,
                          Cart.cart_id==current_user.id).first()
    if c.number != 0:
        c.number -= 1
        db.session.commit()
    return redirect(url_for('show_cart',id=current_user.id))


@app.route('/user-checkout', methods=['POST','GET'])
@login_required
def checkout():
    """
    Checkout Page
    -------------
    """
    form = CheckoutForm()
    c = current_user.cart
    p = [
        Products.query.filter(
        Products.id == i.product_id).first() for i in c]
    return render_template('checkout.html', c=c, p=p, form=form, zip=zip)


@app.route('/user-payment', methods=['POST','GET'])
@login_required
def payment():
    """
    Payment Page
    ------------
    """
    c = current_user.cart
    for i in range(len(c)):
        # reduce product inventory
        Products.query.filter(Products.id==c[i].product_id).first().inventory -= c[i].number - 1
        # add product sold number
        Products.query.filter(Products.id==c[i].product_id).first().sold += c[i].number - 1
    form = CheckoutForm()
    o = Orders.query.filter(Orders.orders_id==current_user.id).first()
    # extracting user info enetred in checkout form
    name = form.name.data
    country = form.country.data
    city = form.city.data
    address = form.address.data
    phone = form.phone.data
    email = form.email.data
    if not o:
        orders = Orders(
            status='در انتظار پرداخت',
            orders_id=current_user.id, total=c[-1].total,
            number=str([c[i].number for i in range(len(c))]),
            product_id=str([c[i].product_id for i in range(len(c))]),
            payment_method='آنلاین', name=name, country=country,
            city=city, address=address, phone=phone, email=email)
        db.session.add(orders)
        db.session.commit()
        for i in c:
            db.session.delete(i)
        db.session.commit()
    if form.payment.data == 'نقدی':
        orders = Orders.query.filter(
            Orders.orders_id==current_user.id).first()
        orders.payment_method = 'نقدی'
        db.session.commit()
        flash('پرداخت موفق')
        return redirect(url_for('main_page'))
    if o:
        flash('این سفارش قبلا ثبت شده است')
        return redirect(url_for('main_page'))
    return redirect(url_for('payment_gateway', name='None'))


@app.route('/payment-gateway/<name>', methods=['POST','GET'])
@login_required
def payment_gateway(name):
    """
    Fake Payment Gateway. *Temporary*
    ---------------------------------
    """
    o = Orders.query.filter(Orders.orders_id==current_user.id).first()
    if name == 'پرداخت':
        order = Orders.query.filter(Orders.orders_id==current_user.id).first()
        order.status = 'پرداخت شده'
        flash('پرداخت موفق')
        db.session.commit()
        return redirect(url_for('main_page'))
    if name == 'انصراف':
        order = Orders.query.filter(
            Orders.orders_id==current_user.id).first()
        order.status = 'کنسل شده'
        flash('عملیات پرداخت کنسل شد')
        db.session.commit()
        return redirect(url_for('main_page'))
    return render_template('gateway.html', o=o)


@app.route('/orders-list', methods=['POST','GET'])
@login_required_role(role="Admin")
def orders_list():
    """
    show all orders | *Avaiable For Admin*
    ---------------
    query the Orders table and find
    all the users that have any order.
    """
    orders = Orders.query.filter(Orders.orders_id==User.id).all()
    users = [User.query.filter(User.id==i.orders_id).first() for i in orders]
    if not orders :
        flash('سفارشی ثبت نشده است')
    return render_template('orders.html', orders=orders, users=users, zip=zip)


@app.route('/order<int:id>', methods=['POST','GET'])
@login_required_role(role="Admin")
def order_line(id):
    """
    show each order details | *Avaiable For Admin*
    ------------------------
    we receive the list of product ID and product's number
    (the number selected by user in the cart ) as a list.
    First we return them from string to list.
    find products using our products id: img title and price will use.
    also show number in template.
    """
    order = Orders.query.filter(Orders.orders_id == id).first()
    products_id = ast.literal_eval(order.product_id)
    products_number = ast.literal_eval(order.number)
    p = [Products.query.filter(Products.id == i).first() for i in products_id]
    return render_template('order_line.html', number=products_number,
                           product=p, order=order, zip=zip)


@app.route('/filter', methods=['POST', 'GET'])
def filter_products():
    form = FilterProductsForm()
    return render_template('filter.html', form=form)


"""
@app.route('/f', methods=['POST', 'GET'])
def filter():
    form = FilterProductsForm()
    global keyword
    keyword = Products.query.filter(
        Products.title.contains(form.keyword.data),
        Products.category == form.category.data,
        Products.price > form.min_price.data,
        Products.price < form.max_price.data
        ).order_by(asc(Products.price)).all()
    return render_template('filter_result.html', keyword=keyword)


@app.route('/popular-filter', methods=['POST', 'GET'])
def popular():
    keyword.sort(key=lambda i: i.rate, reverse=True)
    return render_template('filter_result.html', keyword=keyword)


@app.route('/sold-filter', methods=['POST', 'GET'])
def sold():
    keyword.sort(key=lambda i: i.sold, reverse=True)
    return render_template('filter_result.html', keyword=keyword)


@app.route('/expensive_filter', methods=['POST', 'GET'])
def expensive():
    keyword.sort(key=lambda i: i.price, reverse=True)
    return render_template('filter_result.html', keyword=keyword)


@app.route('/cheapest-filter', methods=['POST', 'GET'])
def cheapest():
    keyword.sort(key=lambda i: i.price)
    return render_template('filter_result.html', keyword=keyword)


@app.route('/newst-filter', methods=['POST', 'GET'])
def newst():
    keyword.sort(key=lambda i: i.date, reverse=True)
    return render_template('filter_result.html', keyword=keyword)
"""


@app.route('/popular', methods=['POST', 'GET'])
def popular_filter():
    keyword = Products.query.order_by(desc(Products.rate)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/most-sold', methods=['POST', 'GET'])
def sold_filter():
    keyword = Products.query.order_by(desc(Products.sold)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/expensive', methods=['POST', 'GET'])
def expensive_filter():
    keyword = Products.query.order_by(desc(Products.price)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/cheapest', methods=['POST', 'GET'])
def cheapest_filter():
    keyword = Products.query.order_by(asc(Products.price)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/new', methods=['POST', 'GET'])
def newst_filter():
    keyword = Products.query.order_by(desc(Products.date)).all()
    return render_template('keyword.html', keyword=keyword)


@app.route('/fa', methods=['GET', 'POST'])
def final_amount():
    """
    Calculate Final Amount
    ----------------------
    """
    c = current_user.cart
    p = [Products.query.filter(Products.id==i.product_id).first() for i in c]
    total = []
    for a, i in zip(c, p):
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


@app.route('/like/<int:id>', methods=['POST','GET'])
def add_rate(id):
    """
    Add Products Rate
    ---------------
    """
    p = Products.query.filter_by(id=id).first()
    p.rate += 1
    db.session.commit()
    flash('امتیاز ثبت شد')
    return redirect(url_for('product_detail', id=id))


@app.route('/dislike/<int:id>', methods=['POST','GET'])
def reduce_rate(id):
    """
    Reduce Product Rate
    ---------------
    """
    p = Products.query.filter_by(id=id).first()
    p.rate -= 1
    db.session.commit()
    flash('امتیاز ثبت شد')
    return redirect(url_for('product_detail', id=id))
