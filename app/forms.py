from wtforms import StringField, SubmitField, MultipleFileField,\
                    PasswordField, TextField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
from app.models import Category, User


def enabled_categories():
    return Category.query.all()


class AddProductForm(FlaskForm):
    photo = FileField('تصویر شاخص:',validators=[FileRequired(),
        FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Images only!')])
    title = StringField('عنوان محصول:', validators=[DataRequired()])
    short_desc = TextAreaField('توضیح کوتاه:', validators=[DataRequired()])
    desc = TextAreaField('توضیحات:', validators=[DataRequired()])
    price = StringField('قیمت:', validators=[DataRequired()])
    discounted = StringField('قیمت تخفیف خورده:')
    inventory = StringField('موجودی:', validators=[DataRequired()])
    category = QuerySelectField('انتخاب دسته بندی:',
        query_factory=enabled_categories, allow_blank=True, validators=[DataRequired()])
    photos = MultipleFileField(
        'تصاویر گالری محصول:',validators=[FileAllowed(
        ['jpg', 'png', 'gif', 'jpeg'], 'Images only!'),
        Length(min=1 , max=5, message="آپلود بیشتر از ۵ فایل مجاز نیست")] )
    submit = SubmitField('Publish')


class AddCategoryForm(FlaskForm):
    name = StringField('نام دسته بندی', validators=[DataRequired()])
    submit = SubmitField('ذخیره')


class FilterProductsForm(FlaskForm):
    keyword = StringField('کلمه کلیدی:')
    category = QuerySelectField(
        'دسته بندی:',query_factory=enabled_categories, allow_blank=True)
    min_price = StringField('از:')
    max_price = StringField('تا')


class RegisterationForm(FlaskForm):
    name = StringField(
        ' نام و نام خانوادگی:', validators=[DataRequired(
        message='لطفا نام خود را وارد کنید')])
    email = StringField(
        'ایمیل:', validators=[DataRequired(message='لطفا ایمیل خود را وارد کنید'),
        Email(check_deliverability=True,message='ایمیل معتبر نیست')])
    password = PasswordField(
        'رمز عبور:', validators=[DataRequired(message='رمز عبور خود را وارد کنید'),
        Length(min=6,max=12,message='رمز عبور باید از ۶ تا ۱۲ کاراکتر طول داشته باشد')])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('این ایمیل قبلا استفاده شده است')


class LoginForm(FlaskForm):
    email = StringField(
        'ایمیل:', validators=[DataRequired(message='لطفا ایمیل خود را وارد کنید'),
        Email(check_deliverability=True,message='ایمیل معتبر نیست')])
    password = PasswordField(
        'رمز عبور:', validators=[DataRequired(message='رمز عبور خود را وارد کنید'),
        Length(min=6, max=12, message='رمز عبور باید از ۶ تا ۱۲ کاراکتر طول داشته باشد')])


class CheckoutForm(FlaskForm):
    name = StringField('نام و نام خانوادگی:', validators=[DataRequired()])
    city =  StringField('شهر:', validators=[DataRequired()])
    address =  TextField('آدرس کامل:', validators=[DataRequired()])
    phone =  StringField('شماره تماس:', validators=[DataRequired()])
    email = StringField('ایمیل:', validators=[DataRequired()])
    payment = RadioField('Label', choices=[('آنلاین'),('نقدی')])
    submit = SubmitField('ثبت شفارش')


class CommentSectionForm(FlaskForm):
    name = StringField('نام:', validators=[DataRequired(message='لطفا نام خود را وارد کنید')])
    email = StringField('ایمیل:', validators=[DataRequired(message='لطفا ایمیل خود را وارد کنید')])
    comment = TextAreaField('دیدگاه:', validators=[DataRequired(message='لطفا دیدگاه خود را بنویسید')])