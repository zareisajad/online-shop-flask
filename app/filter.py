"""
filter products process
"""

from flask import render_template, request
from sqlalchemy import desc, asc

from app import app
from app.models import Products, Category


# pass category to (base.html) template to show in dropdown menu navbar
@app.context_processor
def pass_category():
    # show all categories that has any products in it
    c = Category.query.filter(Category.id == Products.category_id).all()
    return dict(category=c)


@app.route("/filter/category/<category_id>", methods=["POST", "GET"])
def filter_by_category(category_id):
    """
    Filter products by category name
    --------------------------------
    """
    page = request.args.get("page", 1, type=int)
    all_products = Products.query.filter_by(category_id=category_id).paginate(
        page=page, per_page=12
    )
    return render_template("main_page.html", all_products=all_products)


@app.route("/filter/property/<filter_name>", methods=["POST", "GET"])
def filter_by_property(filter_name):
    """
    Filter Products by properties:
    ------------------------------
    most rated, most expensive, cheapest, etc.
    """
    page = request.args.get("page", 1, type=int)
    if filter_name == "محبوبترین":
        all_products = Products.query.order_by(desc(Products.rate)).paginate(
            page=page, per_page=12
        )
    if filter_name == "پرفروشترین":
        all_products = Products.query.order_by(desc(Products.sold)).paginate(
            page=page, per_page=12
        )
    if filter_name == "گرانترین":
        all_products = Products.query.order_by(desc(Products.price)).paginate(
            page=page, per_page=12
        )
    if filter_name == "ارزانترین":
        all_products = Products.query.order_by(asc(Products.price)).paginate(
            page=page, per_page=12
        )
    if filter_name == "جدیدترین":
        all_products = Products.query.order_by(desc(Products.date)).paginate(
            page=page, per_page=12
        )
    return render_template(
        "main_page.html",
        all_products=all_products,
        title=f"فیلتر بر اساس {filter_name}",
    )