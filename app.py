import os
import logging
import jinja2
import markupsafe

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix


# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure SQLite database (for simplicity)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fintelligence.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size

# Custom template filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    """Convert newlines to <br> tags."""
    if not s:
        return ""
    s = str(s)
    return markupsafe.Markup(s.replace('\n', '<br>'))

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize database
db.init_app(app)

with app.app_context():
    # Import models and create tables
    import models  # noqa: F401
    db.create_all()

    # Import and register routes
    from routes import register_routes
    register_routes(app)

# Set up login manager callback
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
