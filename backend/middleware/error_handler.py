from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': str(e)
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'success': False,
            'error': 'Not found',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': str(e)
        }), 409

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # Log the error (in production, use proper logging)
        print(f"Unhandled exception: {str(e)}")

        # Handle custom errors
        if hasattr(e, 'message'):
            return jsonify({
                'success': False,
                'error': type(e).__name__,
                'message': str(e)
            }), 500

        # Generic error response
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
