# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    native_language = db.Column(db.String(5), default='en')
    learning_language = db.Column(db.String(5), default='de')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    vocabulary_items = db.relationship('VocabularyItem', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Book model
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256), nullable=True)
    language = db.Column(db.String(5), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_at = db.Column(db.DateTime, nullable=True)
    last_position = db.Column(db.Integer, default=0)  # Last reading position

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Book {self.title}>'


# Word information cache model
class WordInfo(db.Model):
    __tablename__ = 'word_info'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(5), nullable=False)
    info = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    access_count = db.Column(db.Integer, default=1)

    __table_args__ = (
        db.UniqueConstraint('word', 'language', name='_word_language_uc'),
    )

    def __repr__(self):
        return f'<WordInfo {self.word} ({self.language})>'


# User's vocabulary items
class VocabularyItem(db.Model):
    __tablename__ = 'vocabulary_items'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128), nullable=False)
    context = db.Column(db.Text, nullable=True)  # Sentence or context where word was found
    book_title = db.Column(db.String(256), nullable=True)  # Book where word was found
    notes = db.Column(db.Text, nullable=True)  # User notes about the word
    proficiency = db.Column(db.Integer, default=0)  # 0-5 scale of familiarity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, nullable=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('word', 'user_id', name='_word_user_uc'),
    )

    def __repr__(self):
        return f'<VocabularyItem {self.word}>'


# Reading session model to track reading statistics
class ReadingSession(db.Model):
    __tablename__ = 'reading_sessions'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    words_read = db.Column(db.Integer, default=0)
    words_looked_up = db.Column(db.Integer, default=0)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    def __repr__(self):
        return f'<ReadingSession {self.id}>'


# Chat history model to keep track of conversations with the AI
class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word = db.Column(db.String(128), nullable=True)  # Word that initiated the chat

    def __repr__(self):
        return f'<ChatHistory {self.id}>'