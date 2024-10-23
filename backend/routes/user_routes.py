# routes/user_routes.py
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User
from db import db
import uuid



bcrypt = Bcrypt()

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    if current_user['role'] == 'Security Staff':
        return jsonify({'message': 'Only administrators or assistant administrators can register new users'}), 403

    data = request.get_json()
    required_fields = ['username', 'password', 'role']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Invalid input'}), 400

    if current_user['role'] == 'Assistant Administrator' and data['role'] != 'Security Staff':
        return jsonify({'message': 'You can only register security staff in your current role'}), 403

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()

    # Allow Administrators, Assistant Administrators, and Security Staff to view users
    if current_user['role'] not in ['Administrator', 'Assistant Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    users = User.query.all()
    user_list = [{
        "user_id": user.user_id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role
    } for user in users]
    
    return jsonify(user_list), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
        return jsonify({'message': 'Only administrators or assistant administrators can delete users'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Invalid input'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        # Update device_token if it's not already set
        if 'device_token' in data and data['device_token']:
            user.device_token = data['device_token']
            db.session.commit()

        access_token = create_access_token(identity={
            'username': user.username,
            'role': user.role,
            'device_token': user.device_token
        })
        user_info = {
            'username': user.username,
            'role': user.role,
            'device_token': user.device_token
        }
        return jsonify(access_token=access_token, user_info=user_info), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    profile_data = {
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'phone_number': user.phone_number
    }
    return jsonify(profile_data), 200



@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not bcrypt.check_password_hash(user.password, old_password):
        return jsonify({'success': False, 'message': 'Old password is incorrect'}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully'}), 200