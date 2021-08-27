"""
    all the authentication process and routes relate to user:
    "register", "login", "edit_profile", "user_orders", "user_order_detail"
"""

import ast

from persiantools.jdatetime import JalaliDateTime
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.models import Products, User, Orders, Favorite
from app.forms import RegisterationForm, LoginForm, EditProfileForm


@app.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for("main_page"))
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, role="user")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("ثبت نام انجام شد - وارد حساب کاربری شوید", category="success")
        return redirect(url_for("login"))
    return render_template("users/register.html", form=form, title="ثبت نام")


@app.route("/login", methods=["GET", "POST"])
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
        return redirect(url_for("main_page"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(
                " کاربری با این ایمیل پیدا نشد - ابتدا ثبت نام کنید", category="danger"
            )
            return redirect(url_for("register"))
        if user and not user.check_password(form.password.data):
            flash("رمز عبور اشتباه است", category="danger")
            return redirect(url_for("login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main_page")
        return redirect(next_page)
    return render_template("users/login.html", form=form, title="ورود به حساب کاربری")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main_page"))


@app.route("/user/profile/edit", methods=["GET", "POST"])
@login_required
def edit_user_profile():
    """
    edit user profile
    ------------
    """
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('تغییرات ذخیره شد', category='success')
        return redirect(url_for('edit_user_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('users/edit_user_profile.html', form=form)


@app.route("/user/favorite", methods=["GET", "POST"])
@login_required
def user_favorites():
    favorites = current_user.favorite
    if not favorites:
        flash('لیست علاقه مندی های شما خالی است.', category='info')
    return render_template('users/user_favorites.html', favorites=favorites)


@app.route("/add/user/favorite/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_favorites(product_id):
    if Favorite.query.filter_by(product_id=product_id, user_id=current_user.id).first():
        flash('این محصول قبلا اضافه شده', category='danger')
        return redirect(url_for('user_favorites'))
    fav = Favorite(product_id=product_id, user_id=current_user.id)
    db.session.add(fav)
    db.session.commit()
    return redirect(url_for('user_favorites'))


@app.route("/remove/user/favorite/<int:product_id>", methods=["GET"])
@login_required
def remove_favorite(product_id):
    if request.method == 'GET':
        product = Favorite.query.filter_by(
            product_id=product_id, user_id=current_user.id).first_or_404()
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('user_favorites'))


@app.route("/user/profile/orders", methods=["GET", "POST"])
@login_required
def user_orders():
    orders = current_user.orders
    if not orders:
        flash('لیست سفارشات شما خالی است', category='info')
    return render_template('users/user_orders.html', orders=orders,
                           JalaliDateTime=JalaliDateTime, title="لیست سفارشات",)


@app.route("/user/profile/order/<int:order_id>", methods=["GET", "POST"])
@login_required
def user_order_detail(order_id):
    """
    show each order details
    -----------------------
    we receive the list of product ID and product's number
    (the number selected by user in the cart ) as a list.
    First we return them from string to list.
    find products using our products id: img title and price will use.
    also shown number in template.
    """
    order = Orders.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    products_id = ast.literal_eval(order.product_id)
    products_number = ast.literal_eval(order.number)
    p = [Products.query.filter(Products.id == i).first() for i in products_id]
    return render_template('users/user_order_detail.html', order=order,
                           number=products_number, product=p, zip=zip,
                           JalaliDateTime=JalaliDateTime, title="لیست سفارشات",)
