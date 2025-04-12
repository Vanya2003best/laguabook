# app/forms/book_forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from flask import current_app
from flask_babel import lazy_gettext as _l

class BookUploadForm(FlaskForm):
    """Form for uploading new books"""
    file = FileField(_l('Book File'), validators=[
        FileRequired(),
        # Уберите доступ к current_app.config здесь
        FileAllowed(['txt', 'pdf', 'epub', 'mobi', 'doc', 'docx', 'rtf'],
                   'File format not supported.')
    ])
    title = StringField(_l('Title (Optional)'), validators=[Length(max=256), Optional()])
    author = StringField(_l('Author (Optional)'), validators=[Length(max=256), Optional()])
    language = SelectField(_l('Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    description = TextAreaField(_l('Description (Optional)'), validators=[Length(max=1000), Optional()])
    submit = SubmitField(_l('Upload'))

class BookEditForm(FlaskForm):
    """Form for editing book details"""
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=256)])
    author = StringField(_l('Author'), validators=[Length(max=256), Optional()])
    language = SelectField(_l('Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    description = TextAreaField(_l('Description'), validators=[Length(max=1000), Optional()])
    submit = SubmitField(_l('Save Changes'))

class BookSearchForm(FlaskForm):
    """Form for searching books"""
    query = StringField(_l('Search'), validators=[Optional(), Length(min=2, max=50)])
    language = SelectField(_l('Language'), choices=[
        ('', 'All Languages'),
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ], validators=[Optional()])
    sort_by = SelectField(_l('Sort By'), choices=[
        ('last_read', 'Recently Read'),
        ('created_at', 'Recently Added'),
        ('title', 'Title'),
        ('author', 'Author')
    ], default='last_read')
    submit = SubmitField(_l('Search'))

class ImportUrlForm(FlaskForm):
    """Form for importing books from URL"""
    url = StringField(_l('URL'), validators=[DataRequired(), Length(max=500)])
    language = SelectField(_l('Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    submit = SubmitField(_l('Import'))