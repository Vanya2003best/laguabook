# app/routes/book.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from ..models import db, Book
from ..forms.book_forms import BookUploadForm
from ..services.file_service import FileService

book = Blueprint('book', __name__)
file_service = FileService()
@book.route('/library')
@login_required
def library():
    print("Entering library route")
    books = Book.query.filter_by(user_id=current_user.id).all()
    print(f"Found {len(books)} books")
    return render_template('books/library.html', title='My Library', books=books)


@book.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a new book"""
    form = BookUploadForm()

    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', str(current_user.id))
        os.makedirs(upload_folder, exist_ok=True)

        if not file_service.allowed_file(file.filename):
            flash(f'File type not allowed. Supported types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}',
                  'danger')
            return redirect(request.url)

        book = file_service.save_file(file, current_user.id)

        if book:
            flash(f'Book "{book.title}" uploaded successfully!', 'success')
            return redirect(url_for('book.library'))
        else:
            flash('Error uploading book', 'danger')

    return render_template('books/upload.html', title='Upload Book', form=form)


@book.route('/book/<int:book_id>')
@login_required
def book_details(book_id):
    """Show book details"""
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    return render_template('books/details.html', title=book.title, book=book)


@book.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()

    # Delete file
    if os.path.exists(book.file_path):
        os.remove(book.file_path)

    # Delete database record
    db.session.delete(book)
    db.session.commit()

    flash(f'Book "{book.title}" deleted successfully.', 'success')
    return redirect(url_for('book.library'))


@book.route('/book/<int:book_id>/read')
@login_required
def read_book(book_id):
    """Redirect to reader view for a book"""
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    return redirect(url_for('reader.view', book_id=book.id))