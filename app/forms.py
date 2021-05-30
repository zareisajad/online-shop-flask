from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class AddProductForm(FlaskForm):
    photo = FileField('Photo:',validators=[FileRequired()])
    title = StringField('Title:', validators=[DataRequired()])
    price = StringField('Price:', validators=[DataRequired()])
    discunted = StringField('Discunted Price:', validators=[DataRequired()])
    inventory = StringField('Inventory:', validators=[DataRequired()])
    submit = SubmitField('Publish')