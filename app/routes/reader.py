# app/routes/reader.py
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash
from flask_login import login_required, current_user
from datetime import datetime
import uuid

from ..models import db, Book, ReadingSession, WordInfo, VocabularyItem
from ..services.file_service import FileService
from ..services.ai_service import AIService
from ..models import db, User, Book, VocabularyItem
from ..forms.reader_forms import ExportVocabularyForm
reader = Blueprint('reader', __name__)
file_service = FileService()
ai_service = AIService()


@reader.route('/reader/<int:book_id>')
@login_required
def view(book_id):
    """Reader view for a book"""
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()

    # Update last read timestamp
    book.last_read_at = datetime.utcnow()
    db.session.commit()

    # Create a new reading session
    reading_session = ReadingSession(user_id=current_user.id, book_id=book.id)
    db.session.add(reading_session)
    db.session.commit()

    # Store reading session ID in session
    session['reading_session_id'] = reading_session.id

    # If no chat session ID exists, create one
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())

    # Initialize empty chat history if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []

    # Get text content
    raw_text = file_service.get_text_content(book)
    formatted_text = file_service.format_text_for_reader(raw_text)

    return render_template('reader/view.html',
                           title=book.title,
                           book=book,
                           formatted_text=formatted_text,
                           source_language=book.language,
                           target_language=current_user.native_language)


@reader.route('/reader/end-session', methods=['POST'])
@login_required
def end_session():
    """End the current reading session"""
    if 'reading_session_id' in session:
        reading_session = ReadingSession.query.get(session['reading_session_id'])
        if reading_session and reading_session.user_id == current_user.id:
            reading_session.end_time = datetime.utcnow()
            db.session.commit()
            del session['reading_session_id']

    book_id = request.form.get('book_id')
    if book_id:
        return redirect(url_for('book.book_details', book_id=book_id))
    else:
        return redirect(url_for('book.library'))


@reader.route('/reader/word-info', methods=['POST'])
@login_required
def word_info():
    """Get information about a word"""
    data = request.json
    word = data.get('word')
    source_language = data.get('source_language', 'unknown')
    target_language = data.get('target_language', current_user.native_language)

    if not word:
        return jsonify({'error': 'Word is required'}), 400

    # Increment looked up words count if in a reading session
    if 'reading_session_id' in session:
        reading_session = ReadingSession.query.get(session['reading_session_id'])
        if reading_session and reading_session.user_id == current_user.id:
            reading_session.words_looked_up += 1
            db.session.commit()

    # Get word info from AI service
    info = ai_service.get_word_info(
        word=word,
        source_language=source_language,
        target_language=target_language,
        user_id=current_user.id,
        session_id=session.get('chat_session_id')
    )

    return jsonify(info)


@reader.route('/reader/save-word', methods=['POST'])
@login_required
def save_word():
    """Save a word to user's vocabulary"""
    data = request.json
    word = data.get('word')
    context = data.get('context')
    book_id = data.get('book_id')

    if not word:
        return jsonify({'error': 'Word is required'}), 400

    # Check if word already exists in vocabulary
    vocab_item = VocabularyItem.query.filter_by(
        user_id=current_user.id,
        word=word
    ).first()

    if vocab_item:
        # Update existing entry
        vocab_item.context = context if context else vocab_item.context
        vocab_item.book_id = book_id if book_id else vocab_item.book_id
        vocab_item.last_reviewed = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Word updated in vocabulary', 'id': vocab_item.id})
    else:
        # Create new entry
        book_title = None
        if book_id:
            book = Book.query.get(book_id)
            if book:
                book_title = book.title

        vocab_item = VocabularyItem(
            user_id=current_user.id,
            word=word,
            context=context,
            book_id=book_id,
            book_title=book_title
        )
        db.session.add(vocab_item)
        db.session.commit()
        return jsonify({'message': 'Word added to vocabulary', 'id': vocab_item.id})


@reader.route('/reader/chat', methods=['POST'])
@login_required
def chat():
    """Send a message to the AI assistant"""
    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Ensure chat history exists
    if 'chat_history' not in session:
        session['chat_history'] = []

    # Ensure chat session ID exists
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())

    # Send message to AI service
    response = ai_service.send_chat_message(
        message=message,
        chat_history=session['chat_history'],
        user_id=current_user.id,
        session_id=session['chat_session_id']
    )

    # Update chat history in session
    session['chat_history'].append({'role': 'user', 'content': message})
    session['chat_history'].append({'role': 'assistant', 'content': response['response']})
    session.modified = True

    return jsonify(response)


@reader.route('/reader/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    """Clear the chat history"""
    if 'chat_history' in session:
        session['chat_history'] = []
        session.modified = True

    # Generate a new chat session ID
    session['chat_session_id'] = str(uuid.uuid4())

    return jsonify({'message': 'Chat history cleared'})


@reader.route('/vocabulary')
@login_required
def vocabulary():
    """Show user's vocabulary"""
    vocabulary_items = VocabularyItem.query.filter_by(
        user_id=current_user.id
    ).order_by(VocabularyItem.last_reviewed.desc().nulls_last(),
               VocabularyItem.created_at.desc()).all()

    return render_template(
        'reader/vocabulary.html',
        title='My Vocabulary',
        vocabulary_items=vocabulary_items
    )


@reader.route('/vocabulary/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_vocabulary_item(item_id):
    """Remove a word from vocabulary"""
    item = VocabularyItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()

    return jsonify({'success': True})


@reader.route('/vocabulary/update-proficiency/<int:item_id>', methods=['POST'])
@login_required
def update_proficiency(item_id):
    """Update proficiency level of a vocabulary item"""
    data = request.json
    proficiency = data.get('proficiency')

    item = VocabularyItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.proficiency = int(proficiency)
    item.last_reviewed = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True})


@reader.route('/export-vocabulary', methods=['POST'])
@login_required
def export_vocabulary():
    """Export vocabulary to file"""
    form = ExportVocabularyForm()
    if form.validate_on_submit():
        # Get vocabulary items for current user
        vocabulary_items = VocabularyItem.query.filter_by(user_id=current_user.id).all()

        format = form.format.data
        include_context = form.include_context.data
        include_notes = form.include_notes.data
        include_proficiency = form.include_proficiency.data

        # For now, just return to vocabulary page with message
        flash('Export functionality will be implemented soon.', 'info')
        return redirect(url_for('reader.vocabulary'))

    # If form validation fails, return to vocabulary page
    return redirect(url_for('reader.vocabulary'))