import base64
from app import app, db 
from flask import render_template, flash, redirect, url_for, request
from app.models import Products
from app.forms import AddProductForm
from werkzeug.utils import secure_filename


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


# TODO : Add new data and render seperate for gallery pics.
# Also a new file field in forms. next try to handle it here
@app.route('/add', methods=['POST','GET'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename) # check if can need for secure while read()
        data = f.read()
        render_file = render_picture(data)
        product = Products(data=data, rendered_data=render_file,
                           title=form.title.data, price=form.price.data,
                           discunted=form.discunted.data, 
                           inventory=form.inventory.data)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)


@app.route('/manage', methods=['POST','GET'])
def manage_products():
    products = Products.query.all()
    return render_template('manage_products.html', products=products)


@app.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    del_pic = Products.query.get(id)
    if request.method == 'POST':
        form = request.form['delete']
        if form == 'Delete':
            db.session.delete(del_pic)
            db.session.commit()
            flash('The product is live now!')
            return redirect(url_for('manage_products'))
    return redirect(url_for('manage_products'))