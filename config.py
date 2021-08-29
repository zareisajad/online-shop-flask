"""Class-based application configuration"""
import os
import bleach
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
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    # set size limit for upload files
    MAX_CONTENT_LENGTH = 3 * 1000 * 1000
    # Upload paths
    UPLOAD_PATH = os.path.join('app/static/images')
    UPLOAD_GALLERY = os.path.join('app/static/gallery')
    # bleach config
    ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS + [
        'h1','h2','h3','h4','h5',
        'h6','br','img','font'
    ]
    ALLOWED_ATTRIBUTES = {
        '*': ['style', 'id', 'class'],
        'font': ['color'],
        'a': ['href'],
        'img': ['src', 'alt']
    }
    ALLOWED_STYLES = bleach.sanitizer.ALLOWED_STYLES + [
        'color', 'background-color'
    ]