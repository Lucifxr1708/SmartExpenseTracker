import os
import logging
from flask import Flask
from flask_login import LoginManager
import markupsafe

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after app initialization to avoid circular imports
from models import User

@login_manager.user_loader
def load_user(user_id):
    logging.debug(f"Loading user with ID: {user_id}")
    return User.get(user_id)

# Add Jinja2 filters and utilities after all imports
@app.template_filter('nl2br')
def nl2br(value):
    return markupsafe.Markup(markupsafe.escape(value).replace('\n', '<br>'))

@app.context_processor
def utility_processor():
    from datetime import datetime
    return dict(datetime=datetime)

# Import routes last to avoid circular imports
import routes