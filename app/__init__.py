"""Flask application factory"""

from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'ابتدا وارد حساب کاربری شوید'
login.login_message_category = 'info'

from app import app, routes, errors, users, filter
