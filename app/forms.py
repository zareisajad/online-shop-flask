from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, PasswordField, TextField, IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Category, User


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


class FilterProductsForm(FlaskForm):
    keyword = StringField('Keyword:')
    category = QuerySelectField(
        'Category:',query_factory=enabled_categories, allow_blank=True)
    min_price = StringField('from:')
    max_price = StringField('to')
    

class RegisterationForm(FlaskForm):
    name = StringField(
        'Name And Lastname:', validators=[DataRequired(
        message='please enter your name')])
    email = StringField(
        'Email:', validators=[DataRequired(message='please enter your email'),
        Email(check_deliverability=True,message='email is not valid - try again')])
    password = PasswordField(
        'Password:', validators=[DataRequired(message='Enter your password'),
        Length(min=6,max=12,message='password must be 6 to 12 char')])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already in use.')
    

class LoginForm(FlaskForm): 
    email = StringField(
        'Email:', validators=[DataRequired(message='please enter your email'),
        Email(check_deliverability=True,message='email is not valid - try again')])
    password = PasswordField(
        'Password:', validators=[DataRequired(message='Enter your password'),
        Length(min=6,max=12,message='password must be 6 to 12 char')])
    
    
class CheckoutForm(FlaskForm):
    name = StringField('Name and lastname:', validators=[DataRequired()])
    country = StringField('country:', validators=[DataRequired()])
    city =  StringField('city:', validators=[DataRequired()])
    address =  TextField('Address:', validators=[DataRequired()])
    phone =  StringField('Phone:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired()])