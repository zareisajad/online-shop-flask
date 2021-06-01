from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, length
from flask_wtf.file import FileField, FileRequired, FileAllowed


class AddProductForm(FlaskForm):
    photo = FileField('Photo:',validators=[FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')])
    title = StringField('Title:', validators=[DataRequired(),length(min=1, max=39, message='Too many characters')])
    price = StringField('Price:', validators=[DataRequired()])
    discunted = StringField('Discunted Price:', validators=[DataRequired()])
    inventory = StringField('Inventory:', validators=[DataRequired()])
    photos = MultipleFileField('Add Gallery')
    submit = SubmitField('Publish')