# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '../instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
    OPENAI_PROJECT_ID = os.environ.get('OPENAI_PROJECT_ID')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-4o-mini'

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'epub', 'mobi', 'doc', 'docx', 'rtf'}

    # Application configuration
    APP_NAME = 'LinguaReader'
    LANGUAGES = ['en', 'de', 'fr', 'es', 'it', 'pl', 'ru']
    DEFAULT_LANGUAGE = 'en'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    # Use stronger security settings for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}