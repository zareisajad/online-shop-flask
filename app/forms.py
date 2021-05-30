from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, length
from flask_wtf.file import FileField, FileRequired


class AddProductForm(FlaskForm):
    photo = FileField('Photo:',validators=[FileRequired()])
    title = StringField('Title:', validators=[DataRequired(),length(min=1, max=39, message='Too many characters')])
    price = StringField('Price:', validators=[DataRequired()])
    discunted = StringField('Discunted Price:', validators=[DataRequired()])
    inventory = StringField('Inventory:', validators=[DataRequired()])
    submit = SubmitField('Publish')