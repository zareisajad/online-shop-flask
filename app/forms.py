from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Category


def enabled_categories():
    return Category.query.all()


class AddProductForm(FlaskForm):
    photo = FileField('Photo:',validators=[FileRequired(),
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    title = StringField('Title:', validators=[DataRequired()])
    price = StringField('Price:', validators=[DataRequired()])
    discounted = StringField('Discunted Price:')
    inventory = StringField('Inventory:', validators=[DataRequired()])
    category = QuerySelectField('Category',
        query_factory=enabled_categories, allow_blank=True)
    photos = MultipleFileField(
        'Add Gallery',validators=[FileAllowed(
        ['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    submit = SubmitField('Publish')


class AddCategoryForm(FlaskForm):
    name = StringField('Category name', validators=[DataRequired()])
    submit = SubmitField('Add Category')