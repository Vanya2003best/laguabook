# app/error_handlers.py
from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register error handlers with the Flask application"""

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not found',
                'message': 'The requested resource does not exist'
            }), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': 'The server encountered an internal error'
            }), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def too_many_requests(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Too many requests',
                'message': 'You have exceeded the rate limit'
            }), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(413)
    def request_entity_too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Payload too large',
                'message': 'The file you are trying to upload is too large'
            }), 413
        return render_template('errors/413.html'), 413

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # Log the error
        app.logger.error(f'Unhandled exception: {e}', exc_info=True)

        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500

        # Return HTML for browser requests
        return render_template('errors/500.html'), 500