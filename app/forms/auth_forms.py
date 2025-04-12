# app/forms/auth_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_babel import lazy_gettext as _l

from ..models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        _l('Confirm Password'),
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    native_language = SelectField(_l('Native Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    learning_language = SelectField(_l('Learning Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Username already taken.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Email already registered.'))

    def validate_learning_language(self, learning_language):
        if learning_language.data == self.native_language.data:
            raise ValidationError(_l('Native language and learning language cannot be the same.'))


class ProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(_l('New Password'), validators=[Length(min=8)])
    password2 = PasswordField(
        _l('Confirm New Password'),
        validators=[EqualTo('password', message='Passwords must match')]
    )
    native_language = SelectField(_l('Native Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    learning_language = SelectField(_l('Learning Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    submit = SubmitField(_l('Update Profile'))

    def validate_learning_language(self, learning_language):
        if learning_language.data == self.native_language.data:
            raise ValidationError(_l('Native language and learning language cannot be the same.'))


# app/forms/book_forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import lazy_gettext as _l
from flask import current_app


# app/forms/reader_forms.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_babel import lazy_gettext as _l


class ChatForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField(_l('Send'))


class VocabularyNoteForm(FlaskForm):
    notes = TextAreaField(_l('Notes'), validators=[Length(max=500), Optional()])
    proficiency = SelectField(_l('Proficiency Level'), choices=[
        (0, 'Not Known'), (1, 'Recognize'), (2, 'Understand'),
        (3, 'Can Use'), (4, 'Know Well'), (5, 'Mastered')
    ], coerce=int)
    submit = SubmitField(_l('Save'))


class ReaderSettingsForm(FlaskForm):
    font_size = IntegerField(_l('Font Size'), validators=[NumberRange(min=10, max=36)], default=16)
    line_spacing = SelectField(_l('Line Spacing'), choices=[
        ('1', 'Single'), ('1.5', '1.5 Lines'), ('2', 'Double')
    ], default='1.5')
    theme = SelectField(_l('Theme'), choices=[
        ('light', 'Light'), ('sepia', 'Sepia'), ('dark', 'Dark')
    ], default='light')
    submit = SubmitField(_l('Apply'))