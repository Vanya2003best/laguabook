# app/forms/__init__.py

from .auth_forms import LoginForm, RegistrationForm, ProfileForm
from .book_forms import BookUploadForm, BookEditForm, BookSearchForm, ImportUrlForm
from .reader_forms import (
    ChatForm, VocabularyNoteForm, ReaderSettingsForm,
    TranslationSettingsForm, VocabularyFilterForm, ExportVocabularyForm
)

# This makes the forms available directly from the forms package
# Example: from app.forms import LoginForm