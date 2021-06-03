from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, length
from flask_wtf.file import FileField, FileRequired, FileAllowed


class AddProductForm(FlaskForm):
    photo = FileField('Photo:',validators=[FileRequired(),
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    title = StringField('Title:', validators=[DataRequired()])
    price = StringField('Price:', validators=[DataRequired()])
    discounted = StringField('Discunted Price:')
    inventory = StringField('Inventory:', validators=[DataRequired()])
    photos = MultipleFileField(
        'Add Gallery',validators=[FileAllowed(
        ['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    submit = SubmitField('Publish')