# app/forms/reader_forms.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, IntegerField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_babel import lazy_gettext as _l


class ChatForm(FlaskForm):
    """Form for sending messages to the AI assistant"""
    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField(_l('Send'))


class VocabularyNoteForm(FlaskForm):
    """Form for adding notes to vocabulary items"""
    notes = TextAreaField(_l('Notes'), validators=[Length(max=500), Optional()])
    proficiency = SelectField(_l('Proficiency Level'), choices=[
        (0, 'Not Known'), (1, 'Recognize'), (2, 'Understand'),
        (3, 'Can Use'), (4, 'Know Well'), (5, 'Mastered')
    ], coerce=int)
    submit = SubmitField(_l('Save'))


class ReaderSettingsForm(FlaskForm):
    """Form for reader view settings"""
    font_size = IntegerField(_l('Font Size'), validators=[NumberRange(min=10, max=36)], default=18)
    line_spacing = SelectField(_l('Line Spacing'), choices=[
        ('1', 'Single'), ('1.5', '1.5 Lines'), ('2', 'Double')
    ], default='1.5')
    theme = SelectField(_l('Theme'), choices=[
        ('light', 'Light'), ('sepia', 'Sepia'), ('dark', 'Dark')
    ], default='light')
    submit = SubmitField(_l('Apply'))


class TranslationSettingsForm(FlaskForm):
    """Form for translation and AI assistant settings"""
    source_language = SelectField(_l('Book Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    target_language = SelectField(_l('Your Language'), choices=[
        ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français'),
        ('es', 'Español'), ('it', 'Italiano'), ('pl', 'Polski'), ('ru', 'Русский')
    ])
    auto_save_words = BooleanField(_l('Automatically save looked up words'), default=False)
    show_translations = BooleanField(_l('Show translations in tooltip'), default=True)
    assistant_mode = RadioField(_l('AI Assistant Mode'), choices=[
        ('detailed', 'Detailed (grammar, usage examples, etymology)'),
        ('simple', 'Simple (brief definition and translation)'),
        ('custom', 'Custom (use your own prompt)')
    ], default='detailed')
    custom_prompt = TextAreaField(_l('Custom AI Prompt'), validators=[Length(max=500), Optional()])
    submit = SubmitField(_l('Save Settings'))


class VocabularyFilterForm(FlaskForm):
    """Form for filtering vocabulary items"""
    search = TextAreaField(_l('Search'), validators=[Length(max=100), Optional()])
    proficiency_min = SelectField(_l('Min Proficiency'), choices=[
        (-1, 'Any'), (0, 'Not Known'), (1, 'Recognize'), (2, 'Understand'),
        (3, 'Can Use'), (4, 'Know Well')
    ], coerce=int, default=-1)
    proficiency_max = SelectField(_l('Max Proficiency'), choices=[
        (5, 'Any'), (0, 'Not Known'), (1, 'Recognize'), (2, 'Understand'),
        (3, 'Can Use'), (4, 'Know Well'), (5, 'Mastered')
    ], coerce=int, default=5)
    book_id = SelectField(_l('Book'), coerce=int)
    sort_by = SelectField(_l('Sort By'), choices=[
        ('last_reviewed', 'Recently Reviewed'),
        ('created_at', 'Recently Added'),
        ('word', 'Alphabetical'),
        ('proficiency', 'Proficiency Level')
    ], default='last_reviewed')
    submit = SubmitField(_l('Filter'))

    def __init__(self, *args, books=None, **kwargs):
        super(VocabularyFilterForm, self).__init__(*args, **kwargs)
        if books:
            self.book_id.choices = [(0, 'All Books')] + [(book.id, book.title) for book in books]
        else:
            self.book_id.choices = [(0, 'All Books')]
        self.book_id.default = 0


class ExportVocabularyForm(FlaskForm):
    """Form for exporting vocabulary"""
    format = SelectField(_l('Export Format'), choices=[
        ('csv', 'CSV (Excel, Google Sheets)'),
        ('txt', 'Text File'),
        ('anki', 'Anki Deck'),
        ('pdf', 'PDF Document')
    ], default='csv')
    include_context = BooleanField(_l('Include context'), default=True)
    include_notes = BooleanField(_l('Include notes'), default=True)
    include_proficiency = BooleanField(_l('Include proficiency levels'), default=True)
    submit = SubmitField(_l('Export'))