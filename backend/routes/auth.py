from flask import Blueprint, request, jsonify
from models.user import User
from middleware.auth import generate_token, auth_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Extract data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validate input
        errors = User.validate_registration(name, email, password)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': errors
            }), 400

        # Create user
        try:
            user = User.create(name, email, password)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409

        # Generate token
        token = generate_token(user['_id'])

        # Return response
        return jsonify({
            'success': True,
            'token': token,
            'user': User.to_dict(user)
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        # Extract data
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validate input
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400

        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Verify password
        if not User.verify_password(password, user['password']):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Generate token
        token = generate_token(user['_id'])

        # Return response
        return jsonify({
            'success': True,
            'token': token,
            'user': User.to_dict(user)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Login failed',
            'message': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """Get current authenticated user"""
    try:
        user = request.current_user

        return jsonify({
            'success': True,
            'user': User.to_dict(user)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user',
            'message': str(e)
        }), 500
