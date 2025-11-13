from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
from models.user import User

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET', 'your_super_secret_jwt_key_change_this_in_production')

def generate_token(user_id):
    """Generate JWT token for user"""
    import datetime

    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def auth_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        # Extract token
        token = auth_header.split(' ')[1]

        # Verify token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401

        # Get user from database
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 401

        # Add user to request context
        request.current_user = user
        request.user_id = str(user['_id'])

        return f(*args, **kwargs)

    return decorated_function

def optional_auth(f):
    """Decorator for routes where auth is optional"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_id = verify_token(token)

            if user_id:
                user = User.find_by_id(user_id)
                if user:
                    request.current_user = user
                    request.user_id = str(user['_id'])

        return f(*args, **kwargs)

    return decorated_function
