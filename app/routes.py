import os
import ast
import datetime

from functools import wraps
from persiantools.jdatetime import JalaliDateTime
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse

from app import app, db
from app.models import Products, Cart, Gallery, Category, \
    User, Orders, Comments
from app.forms import AddProductForm, AddCategoryForm, \
    RegisterationForm, LoginForm, CheckoutForm, CommentSectionForm


def login_required_role(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(404)
            if current_user.role != role and role != "ANY":
                abort(404)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# pass category to (base.html) template to show in dropdown menu navbar
@app.context_processor
def pass_category():
    # show all categories that has any products in it 
    c = Category.query.filter(Category.id == Products.category_id).all()
    return dict(category=c)


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
        flash('ثبت نام انجام شد - وارد حساب کاربری شوید', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='ثبت نام')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login User
    ----------
    first if user is already logged in, we redirect them to main page
    after extract email and password from login form;
    we check if the email is in db or not, otherwise app flashes a message
    also we compare the given password with decoded hash that is in database.
    check_password defined in forms.py
    """
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(' کاربری با این ایمیل پیدا نشد - ابتدا ثبت نام کنید',
                  category='danger')
            return redirect(url_for('register'))
        if user and not user.check_password(form.password.data):
            flash('رمز عبور اشتباه است', category='danger')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_page')
        return redirect(next_page)
    return render_template(
        'login.html', form=form, title="ورود به حساب کاربری")


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
    page = request.args.get('page', 1, type=int)
    all_products = Products.query.paginate(page=page, per_page=20)
    if not all_products.items:
        flash('محصولی موجود نیست', category='info')
    return render_template(
        'main_page.html', all_products=all_products, title='محصولات')


@app.route('/add/product', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def add_product():
    """
    Add New Product | *Available For Admin*
    ---------------
    """
    form = AddProductForm()
    if request.method == "POST":
        if form.validate_on_submit():
            c = Category.query.filter_by(name=str(form.category.data)).first()
            uploaded_file = form.photo.data
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(
                os.path.join(app.config['UPLOAD_PATH'], filename)
            )
            url = (os.path.join('/images', filename))
            p = Products(
                title=form.title.data, price=form.price.data,
                discounted=form.discounted.data, sold=0, rate=0,
                short_desc=form.short_desc.data, desc=form.desc.data,
                inventory=form.inventory.data, photo=url, category_id=c.id
            )
            db.session.add(p)
            db.session.commit()
            images = form.photos.data
            for img in images:
                filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_GALLERY'], filename))
                url = (os.path.join('/gallery', filename))
                files = Gallery(pics=url, p_id=p.id)
                db.session.add(files)
            db.session.commit()
            return redirect(url_for('main_page'))
    return render_template(
        'add_product.html', form=form, title='ایجاد محصول جدید')


@app.route('/add/category', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def add_category():
    """
    Add New Category | *Available For Admin*
    ----------------
    """
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('دسته بندی جدید ایجاد شد', category='info')
        return redirect(url_for('add_product'))
    category = Category.query.all()
    return render_template('add_category.html', form=form,
                           category=category, title='ایجاد دسته بندی جدید')


@app.route('/manage', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def manage_products():
    """
    Manage Products Page | *Available For Admin*
    --------------------
    """
    all_products = Products.query.all()
    if not all_products:
        flash('محصولی موجود نیست', category='info')
    return render_template(
        'manage_products.html', products=all_products, title='مدیریت محصولات')


@app.route('/delete/product/<int:product_id>', methods=['GET', 'POST'])
@login_required_role(role="Admin")
def delete(product_id):
    """
    Delete Products | *Available For Admin*
    ---------------
    """
    g = Gallery.query.all()
    for i in g:
        if i.p_id == product_id:
            name = i.pics.split('/')[2]
            db.session.delete(i)
            os.remove(app.config['UPLOAD_GALLERY'] + '/' + name)
    product = Products.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    name = product.photo.split('/')[2]
    os.remove(app.config['UPLOAD_PATH'] + '/' + name)
    c = Cart.query.get(product_id)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('manage_products'))


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    """
    Products Details
    ---------------
    """
    form = CommentSectionForm()
    product = Products.query.filter_by(id=product_id).first()
    gallery = Gallery.query.all()
    return render_template('product_detail.html', product=product,
                           gallery=gallery, title=product.title, form=form,
                           JalaliDateTime=JalaliDateTime)


@app.route('/add/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def comments(id):
    form = CommentSectionForm()
    if form.validate_on_submit():
        comment = Comments(
            name=form.name.data,
            email=form.email.data,
            comment=form.comment.data,
            create_date=datetime.datetime.now(),
            product_id=id
        )
        db.session.add(comment)
        flash(' دیدگاه شما ثبت شد', category='success')
    db.session.commit()
    return redirect(url_for('product_detail', product_id=id))


@app.route('/add/cart/<int:id>', methods=['POST', 'GET'])
@login_required
def cart(id):
    """ 
    Add product to user cart
    ------------------------
    """
    # if a product inventory is 0, we don't add it to cart
    if Products.query.filter(Products.id == id).first().inventory == 0:
        flash('این محصول موجود نیست', category='danger')
        return redirect(url_for('main_page'))
    # check if the product is already in cart
    ca = Cart.query.filter(
        Cart.product_id == id, Cart.cart_id == current_user.id).first()
    if ca:
        flash('این محصول قبلا اضافه شده است', category='danger')
        return redirect(url_for('show_cart'))
    else:
        # number input in product detail page
        n = request.form.get('number')
        c = Cart(
            product_id=id, number=n, amount=0,
            total=0, cart_id=current_user.id
        )
        db.session.add(c)
        flash('به سبد خرید اضافه شد', category='success')
        # if product add from main page-there is no input number so number is 1
        if not n:
            c.number = 1
    db.session.commit()
    return redirect(url_for('main_page'))


@app.route('/cart', methods=['POST', 'GET'])
@login_required
def show_cart():
    """
    User Cart
    ---------
    """
    user_cart = current_user.cart
    if not user_cart:
        flash('سبد خرید شما خالی است', category='info')
    cart_products = [
        Products.query.filter(Products.id == i.product_id).first()
        for i in current_user.cart]
    return render_template(
        'cart.html', cart_products=cart_products,
        user_cart=user_cart, zip=zip, title='سبد خرید'
    )


@app.route('/delete/cart/product/<int:id>', methods=['GET', 'POST'])
def delete_cart(id):
    """
    Remove Items From Cart
    ----------------------
    """
    c = Cart.query.filter(
        Cart.cart_id == current_user.id, Cart.product_id == id
    ).first()
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('show_cart', id=current_user.id))


@app.route('/add/cart/number/<int:product_id>', methods=['POST', 'GET'])
def add_num(product_id):
    """
    Add Product Number In Cart
    --------------------------
    """
    c = Cart.query.filter(Cart.product_id == product_id,
                          Cart.cart_id == current_user.id).first()
    p = Products.query.filter(Products.id == product_id).first()
    while c.number < p.inventory:
        c.number += 1
        db.session.commit()
        return redirect(url_for('show_cart'))
    else:
        flash('بیشتر از این تعداد موجود نیست', category='danger')
        return redirect(url_for('show_cart'))


@app.route('/reduce/cart/number/<int:product_id>', methods=['POST', 'GET'])
def reduce_num(product_id):
    """
    Reduce Product Number In Cart
    -----------------------------
    """
    c = Cart.query.filter(Cart.product_id == product_id,
                          Cart.cart_id == current_user.id).first()
    if c.number > 1:
        c.number -= 1
        db.session.commit()
    # if number in cart == 0, remove item from cart
    else:
        return redirect(url_for('delete_cart', id=product_id))
    return redirect(url_for('show_cart'))


@app.route('/checkout', methods=['POST', 'GET'])
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
    return render_template('checkout.html', c=c, p=p, form=form,
                           zip=zip, title='ثبت سفارش')


@app.route('/payment', methods=['POST', 'GET'])
@login_required
def payment():
    """
    Payment Page
    ------------
    """
    user_cart = current_user.cart
    # extracting user info entered in checkout form
    form = CheckoutForm()
    name = form.name.data
    city = form.city.data
    address = form.address.data
    phone = form.phone.data
    email = form.email.data
    # insert user order's data to Orders table 
    orders = Orders(
        status='در انتظار پرداخت',
        orders_id=current_user.id, payment_method='آنلاین',
        name=name, city=city, address=address, phone=phone,
        email=email, total=user_cart[-1].total,
        create_order_date=datetime.datetime.now(),
        number=str(
            [user_cart[i].number for i in range(len(user_cart))]),
        product_id=str(
            [user_cart[i].product_id for i in range(len(user_cart))])
    )
    db.session.add(orders)
    db.session.commit()
    # find user order 
    orders = Orders.query.filter(Orders.orders_id == current_user.id).first()
    # if user select cash *نقدی* option in form
    if form.payment.data == 'نقدی':
        for i in range(len(user_cart)):
            # reduce product inventory
            Products.query.filter(
                Products.id == user_cart[i].product_id
            ).first().inventory -= user_cart[i].number
            # add product sold number
            Products.query.filter(
                Products.id == user_cart[i].product_id
            ).first().sold += user_cart[i].number
        # change payment status to 'نقدی', which was 'آنلاین'
        orders.payment_method = 'نقدی'
        flash('سفارش ثبت شد', category='success')
        # delete user cart's items
        for i in user_cart:
            db.session.delete(i)
        db.session.commit()
        return redirect(url_for('main_page'))

    # track date and time when user goes to payment gateway
    orders.start_payment_date = datetime.datetime.now()
    db.session.commit()
    return redirect(url_for('payment_gateway', name='None'))


@app.route('/payment-gateway/<name>', methods=['POST', 'GET'])
@login_required
def payment_gateway(name):
    """
    Fake Payment Gateway. *Temporary*
    ---------------------------------
    """
    o = Orders.query.filter(Orders.orders_id == current_user.id).first()
    if name == 'پرداخت':
        c = current_user.cart
        for i in range(len(c)):
            # reduce product inventory
            Products.query.filter(
                Products.id == c[i].product_id).first().inventory -= c[i].number
            # add product sold number
            Products.query.filter(
                Products.id == c[i].product_id).first().sold += c[i].number
        for i in c:
            db.session.delete(i)
        order = Orders.query.filter(Orders.orders_id == current_user.id).first()
        order.status = 'پرداخت شده'
        order.finish_payment_date = datetime.datetime.now()
        flash('پرداخت موفق', category='success')
        db.session.commit()
        return redirect(url_for('main_page'))
    if name == 'انصراف':
        order = Orders.query.filter(
            Orders.orders_id == current_user.id).first()
        order.status = 'کنسل شده'
        flash('عملیات پرداخت کنسل شد', category='danger')
        db.session.commit()
        return redirect(url_for('main_page'))
    return render_template('gateway.html', o=o, title='پرداخت')


@app.route('/orders', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def orders_list():
    """
    show all orders | *Available For Admin*
    ---------------
    query the Orders table and find
    all the users that have any order.
    """
    orders = Orders.query.filter(Orders.orders_id == User.id).all()
    users = [User.query.filter(User.id == i.orders_id).first() for i in orders]
    if not orders:
        flash('سفارشی ثبت نشده است', category='info')
    return render_template(
        'orders.html', orders=orders, users=users, zip=zip,
        JalaliDateTime=JalaliDateTime, title='لیست سفارشات')


@app.route('/order<int:order_id>', methods=['POST', 'GET'])
@login_required_role(role="Admin")
def order_line(order_id):
    """
    show each order details | *Available For Admin*
    -----------------------------------------------
    we receive the list of product ID and product's number
    (the number selected by user in the cart ) as a list.
    First we return them from string to list.
    find products using our products id: img title and price will use.
    also shown number in template.
    """
    order = Orders.query.filter(Orders.orders_id == order_id).first()
    products_id = ast.literal_eval(order.product_id)
    products_number = ast.literal_eval(order.number)
    p = [Products.query.filter(Products.id == i).first() for i in products_id]
    return render_template(
        'order_line.html', number=products_number, product=p,
        order=order, zip=zip, JalaliDateTime=JalaliDateTime, title='جزئیات سفارش')


@app.route('/filter/category/<category_id>', methods=['POST', 'GET'])
def filter_by_category(category_id):
    """
    Filter products by category name
    --------------------------------
    """
    page = request.args.get('page', 1, type=int)
    all_products = Products.query.filter_by(
        category_id=category_id).paginate(page=page, per_page=20)
    return render_template(
        'main_page.html', all_products=all_products)


@app.route('/filter/property/<filter_name>', methods=['POST', 'GET'])
def filter_by_property(filter_name):
    """
    Filter Products by properties:
    ------------------------------
    most rated, most expensive, cheapest, etc.
    """
    page = request.args.get('page', 1, type=int)
    if filter_name == 'محبوبترین':
        all_products = Products.query.order_by(
            desc(Products.rate)).paginate(page=page, per_page=20)
    if filter_name == 'پرفروشترین':
        all_products = Products.query.order_by(
            desc(Products.sold)).paginate(page=page, per_page=20)
    if filter_name == 'گرانترین':
        all_products = Products.query.order_by(
            desc(Products.price)).paginate(page=page, per_page=20)
    if filter_name == 'ارزانترین':
        all_products = Products.query.order_by(
            asc(Products.price)).paginate(page=page, per_page=20)
    if filter_name == 'جدیدترین':
        all_products = Products.query.order_by(
            desc(Products.date)).paginate(page=page, per_page=20)
    return render_template('main_page.html', all_products=all_products,
                           title=f'فیلتر بر اساس {filter_name}')


@app.route('/fa', methods=['GET', 'POST'])
def final_amount():
    """
    Calculate Final Amount
    ----------------------
    """
    c = current_user.cart
    p = [Products.query.filter(Products.id == i.product_id).first() for i in c]
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


@app.route('/product/rate/<int:product_id>/<string:name>')
def product_rate(product_id, name):
    """
    Add Products Rate
    ---------------
    """
    if name == 'add':
        p = Products.query.filter_by(id=product_id).first()
        p.rate += 1
    if name == 'reduce':
        p = Products.query.filter_by(id=product_id).first()
        p.rate -= 1
    db.session.commit()
    flash('امتیاز ثبت شد', category='success')
    return redirect(url_for('product_detail', product_id=product_id))
