from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User


def role_required(*roles):
    """Decorator: verify JWT and check user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if not user.is_active or user.is_blacklisted:
                return jsonify({'error': 'Account is deactivated or blacklisted'}), 403
            if user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)
