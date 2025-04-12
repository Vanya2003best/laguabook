# app/__init__.py
import datetime
import os
import logging
import uuid
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, g, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_babel import Babel

from .config import config
from .models import db, User
from .error_handlers import register_error_handlers
from flask import Flask

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

migrate = Migrate()
csrf = CSRFProtect()
sess = Session()
babel = Babel()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    sess.init_app(app)
    babel.init_app(app)

    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes.auth import auth as auth_blueprint
    from .routes.book import book as book_blueprint
    from .routes.reader import reader as reader_blueprint
    from .routes.api import api as api_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(book_blueprint, url_prefix='/books')
    app.register_blueprint(reader_blueprint, url_prefix='/reader')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register error handlers
    register_error_handlers(app)

    # Set up logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/linguareader.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('LinguaReader startup')

    # Babel locale selector
    @babel.localeselector
    def get_locale():
        # Try to get the locale from the session, then from the user, then from the request
        if 'locale' in session:
            return session['locale']
        if current_user.is_authenticated:
            return current_user.native_language
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    # Language switcher route
    @app.route('/set-locale/<code>')
    def set_locale(code):
        if code in app.config['LANGUAGES']:
            session['locale'] = code
            if current_user.is_authenticated:
                current_user.native_language = code
                db.session.commit()
        return redirect(request.referrer or url_for('book.library'))

    # Before request handlers
    @app.before_request
    def before_request():
        # Ensure 'chat_session_id' is in the session
        if 'chat_session_id' not in session:
            session['chat_session_id'] = str(uuid.uuid4())

        # Initialize empty chat history if not exists
        if 'chat_history' not in session:
            session['chat_history'] = []

        # Make current time available to templates
        g.current_year = datetime.datetime.now().year

    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='medium'):
        if format == 'full':
            format = "EEEE, d. MMMM y 'at' HH:mm"
        elif format == 'medium':
            format = "EE dd.MM.y HH:mm"
        elif format == 'short':
            format = "dd.MM.y"
        return babel.dates.format_datetime(value, format)

    # Context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.utcnow}

    # Custom jinja filters
    @app.template_filter('language_name')
    def language_name_filter(code):
        languages = {
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pl': 'Polish',
            'ru': 'Russian'
        }
        return languages.get(code, code)

    @app.template_filter('language_color')
    def language_color_filter(code):
        return {
            'en': 'primary',
            'de': 'purple',
            'fr': 'danger',
            'es': 'warning',
            'it': 'success',
            'pl': 'info',
            'ru': 'secondary'
        }.get(code, 'primary')

    return app