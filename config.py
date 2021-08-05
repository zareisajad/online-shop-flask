"""Class-based application configuration"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """
    Flask application config
    ------------------------
    """
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') #File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Avoids SQLAlchemy warning

    # Upload paths
    UPLOAD_PATH = os.path.join('app/static/images')
    UPLOAD_GALLERY = os.path.join('app/static/gallery')

    # Flask-User settings
    USER_APP_NAME = "بازدید سایت"
    USER_ENABLE_EMAIL = True # Enable email authentication
    USER_ENABLE_USERNAME = False # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
