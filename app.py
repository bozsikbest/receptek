import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "lsadifhsikdjvbkjsdbv")  # Fallback for development

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the extensions
db.init_app(app)
# Configure SocketIO with async_mode='eventlet' for better compatibility with Gunicorn
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Register blueprints
from routes.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from routes.admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix='/admin')

from routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
