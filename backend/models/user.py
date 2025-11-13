from datetime import datetime
from bson import ObjectId
import bcrypt
from config.db import get_database

class User:
    collection = None

    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            db = get_database()
            cls.collection = db.users
        return cls.collection

    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hashed password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    @classmethod
    def create(cls, name, email, password):
        """Create a new user"""
        collection = cls.get_collection()

        # Check if user exists
        if collection.find_one({'email': email.lower()}):
            raise ValueError('User with this email already exists')

        user_data = {
            'name': name.strip(),
            'email': email.lower(),
            'password': cls.hash_password(password),
            'totalPurchases': 0,
            'fastestCheckout': None,
            'createdAt': datetime.utcnow()
        }

        result = collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id

        return user_data

    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        collection = cls.get_collection()
        return collection.find_one({'email': email.lower()})

    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return collection.find_one({'_id': user_id})

    @classmethod
    def update(cls, user_id, update_data):
        """Update user data"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        result = collection.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @classmethod
    def update_purchases(cls, user_id, amount, checkout_time=None):
        """Update user's total purchases and fastest checkout"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        update_data = {
            '$inc': {'totalPurchases': amount}
        }

        # Update fastest checkout if provided and better than current
        if checkout_time is not None:
            user = cls.find_by_id(user_id)
            if user['fastestCheckout'] is None or checkout_time < user['fastestCheckout']:
                update_data['$set'] = {'fastestCheckout': checkout_time}

        collection.update_one({'_id': user_id}, update_data)

    @classmethod
    def to_dict(cls, user):
        """Convert user document to dictionary (remove password)"""
        if not user:
            return None

        return {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'totalPurchases': user.get('totalPurchases', 0),
            'fastestCheckout': user.get('fastestCheckout'),
            'createdAt': user.get('createdAt', datetime.utcnow()).isoformat()
        }

    @classmethod
    def validate_registration(cls, name, email, password):
        """Validate registration data"""
        errors = []

        if not name or len(name.strip()) < 2:
            errors.append({'field': 'name', 'message': 'Name must be at least 2 characters'})

        if not email or '@' not in email:
            errors.append({'field': 'email', 'message': 'Valid email is required'})

        if not password or len(password) < 6:
            errors.append({'field': 'password', 'message': 'Password must be at least 6 characters'})

        return errors
