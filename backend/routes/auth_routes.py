from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active or user.is_blacklisted:
        return jsonify({'error': 'Your account has been deactivated. Contact admin.'}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    for field in ['username', 'email', 'password']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email is already registered'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username is already taken'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        role='user',
        full_name=data.get('full_name', ''),
        phone=data.get('phone', ''),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200
