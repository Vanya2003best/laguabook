from flask import Blueprint, render_template

library_bp = Blueprint('library', __name__)

@library_bp.route('/books/library')
def library():
    """Маршрут для страницы библиотеки без авторизации"""
    return render_template('library.html')