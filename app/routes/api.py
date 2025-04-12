# app/routes/api.py
from flask import Blueprint, jsonify, request, current_app, session
from flask_login import login_required, current_user
from datetime import datetime
import uuid

from ..models import db, WordInfo, VocabularyItem, Book
from ..services.ai_service import AIService

api = Blueprint('api', __name__)
ai_service = AIService()

@api.route('/word-info', methods=['POST'])
@login_required
def get_word_info():
    """API endpoint to get information about a word"""
    data = request.json
    word = data.get('word')
    context = data.get('context')
    book_id = data.get('book_id')
    source_language = data.get('source_language', current_user.learning_language)
    target_language = data.get('target_language', current_user.native_language)

    if not word:
        return jsonify({'error': 'Word is required'}), 400

    # Ensure we have a chat session ID
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())

    # Get word info from AI service
    result = ai_service.get_word_info(
        word=word,
        source_language=source_language,
        target_language=target_language,
        user_id=current_user.id,
        session_id=session.get('chat_session_id')
    )

    # Check if word is in user's vocabulary
    in_vocabulary = VocabularyItem.query.filter_by(
        user_id=current_user.id,
        word=word
    ).first() is not None

    # Add context information to response
    result['in_vocabulary'] = in_vocabulary

    # If context is provided, add it to response
    if context:
        result['context'] = context

    # If book_id is provided, add book title to response
    if book_id:
        book = Book.query.get(book_id)
        if book and book.user_id == current_user.id:
            result['book_title'] = book.title

    return jsonify(result)


@api.route('/chat', methods=['POST'])
@login_required
def chat():
    """API endpoint to chat with the AI assistant"""
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

    # Get system prompt based on user's languages
    system_prompt = f"You are a helpful language learning assistant for {current_app.config['LANGUAGES'].get(current_user.learning_language, 'foreign language')} learners. The user's native language is {current_app.config['LANGUAGES'].get(current_user.native_language, 'unknown')}."

    # Add system message if chat history is empty
    if not session['chat_history']:
        session['chat_history'].append({'role': 'system', 'content': system_prompt})

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


@api.route('/vocabulary/add', methods=['POST'])
@login_required
def add_to_vocabulary():
    """API endpoint to add a word to user's vocabulary"""
    data = request.json
    word = data.get('word')
    context = data.get('context')
    book_id = data.get('book_id')
    notes = data.get('notes')

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
        vocab_item.notes = notes if notes else vocab_item.notes
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
            book_title=book_title,
            notes=notes
        )
        db.session.add(vocab_item)
        db.session.commit()
        return jsonify({'message': 'Word added to vocabulary', 'id': vocab_item.id})


@api.route('/vocabulary/remove', methods=['POST'])
@login_required
def remove_from_vocabulary():
    """API endpoint to remove a word from user's vocabulary"""
    data = request.json
    word = data.get('word')

    if not word:
        return jsonify({'error': 'Word is required'}), 400

    # Find and delete vocabulary item
    vocab_item = VocabularyItem.query.filter_by(
        user_id=current_user.id,
        word=word
    ).first()

    if vocab_item:
        db.session.delete(vocab_item)
        db.session.commit()
        return jsonify({'message': 'Word removed from vocabulary'})
    else:
        return jsonify({'error': 'Word not found in vocabulary'}), 404


@api.route('/vocabulary/list', methods=['GET'])
@login_required
def list_vocabulary():
    """API endpoint to list user's vocabulary"""
    # Get query parameters
    sort_by = request.args.get('sort_by', 'last_reviewed')
    order = request.args.get('order', 'desc')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Build query
    query = VocabularyItem.query.filter_by(user_id=current_user.id)

    # Apply sorting
    if sort_by == 'last_reviewed':
        if order == 'desc':
            query = query.order_by(VocabularyItem.last_reviewed.desc().nulls_last())
        else:
            query = query.order_by(VocabularyItem.last_reviewed.asc().nulls_first())
    elif sort_by == 'created_at':
        if order == 'desc':
            query = query.order_by(VocabularyItem.created_at.desc())
        else:
            query = query.order_by(VocabularyItem.created_at.asc())
    elif sort_by == 'word':
        if order == 'desc':
            query = query.order_by(VocabularyItem.word.desc())
        else:
            query = query.order_by(VocabularyItem.word.asc())
    elif sort_by == 'proficiency':
        if order == 'desc':
            query = query.order_by(VocabularyItem.proficiency.desc())
        else:
            query = query.order_by(VocabularyItem.proficiency.asc())

    # Apply pagination
    total = query.count()
    items = query.limit(limit).offset(offset).all()

    # Format response
    result = {
        'items': [
            {
                'id': item.id,
                'word': item.word,
                'context': item.context,
                'book_title': item.book_title,
                'notes': item.notes,
                'proficiency': item.proficiency,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'last_reviewed': item.last_reviewed.isoformat() if item.last_reviewed else None
            }
            for item in items
        ],
        'total': total,
        'page': offset // limit + 1 if limit > 0 else 1,
        'pages': (total + limit - 1) // limit if limit > 0 else 1
    }

    return jsonify(result)


@api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """API endpoint to get user's language learning statistics"""
    # Books statistics
    books_count = Book.query.filter_by(user_id=current_user.id).count()
    total_words = Book.query.filter_by(user_id=current_user.id).with_entities(
        db.func.sum(Book.word_count)).scalar() or 0

    # Vocabulary statistics
    vocabulary_count = VocabularyItem.query.filter_by(user_id=current_user.id).count()

    # Reading sessions statistics
    from ..models import ReadingSession
    total_sessions = ReadingSession.query.filter_by(user_id=current_user.id).count()
    total_reading_time = db.session.query(
        db.func.sum(
            db.func.coalesce(
                db.func.julianday(ReadingSession.end_time) -
                db.func.julianday(ReadingSession.start_time),
                0
            ) * 24 * 60  # Convert to minutes
        )
    ).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.end_time != None
    ).scalar() or 0

    # Words looked up statistics
    total_lookups = db.session.query(
        db.func.sum(ReadingSession.words_looked_up)
    ).filter(
        ReadingSession.user_id == current_user.id
    ).scalar() or 0

    # User's proficiency statistics
    proficiency_distribution = db.session.query(
        VocabularyItem.proficiency,
        db.func.count(VocabularyItem.id)
    ).filter(
        VocabularyItem.user_id == current_user.id
    ).group_by(
        VocabularyItem.proficiency
    ).all()

    proficiency_stats = {level: count for level, count in proficiency_distribution}

    # Format response
    result = {
        'books': {
            'count': books_count,
            'total_words': total_words
        },
        'vocabulary': {
            'count': vocabulary_count,
            'proficiency_distribution': proficiency_stats
        },
        'reading': {
            'sessions': total_sessions,
            'minutes': round(total_reading_time, 1),
            'words_looked_up': total_lookups
        }
    }

    return jsonify(result)


@api.route('/settings', methods=['GET', 'PUT'])
@login_required
def user_settings():
    """API endpoint to get or update user settings"""
    if request.method == 'GET':
        # Return current user settings
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'native_language': current_user.native_language,
            'learning_language': current_user.learning_language
        })

    elif request.method == 'PUT':
        # Update user settings
        data = request.json

        if 'native_language' in data:
            current_user.native_language = data['native_language']

        if 'learning_language' in data:
            current_user.learning_language = data['learning_language']

        db.session.commit()

        return jsonify({
            'message': 'Settings updated successfully',
            'username': current_user.username,
            'email': current_user.email,
            'native_language': current_user.native_language,
            'learning_language': current_user.learning_language
        })


@api.route('/search', methods=['GET'])
@login_required
def search():
    """API endpoint to search books and vocabulary"""
    query = request.args.get('q', '')

    if not query or len(query) < 2:
        return jsonify({
            'books': [],
            'vocabulary': []
        })

    # Search books
    books = Book.query.filter(
        Book.user_id == current_user.id,
        db.or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%')
        )
    ).limit(10).all()

    # Search vocabulary
    vocabulary = VocabularyItem.query.filter(
        VocabularyItem.user_id == current_user.id,
        db.or_(
            VocabularyItem.word.ilike(f'%{query}%'),
            VocabularyItem.notes.ilike(f'%{query}%')
        )
    ).limit(10).all()

    # Format response
    result = {
        'books': [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'language': book.language
            }
            for book in books
        ],
        'vocabulary': [
            {
                'id': item.id,
                'word': item.word,
                'context': item.context,
                'book_title': item.book_title
            }
            for item in vocabulary
        ]
    }

    return jsonify(result)