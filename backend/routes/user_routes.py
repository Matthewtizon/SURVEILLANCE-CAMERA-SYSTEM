# routes/user_routes.py
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User
from db import db
from notifications import *
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

bcrypt = Bcrypt()

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    if current_user['role'] == 'Security Staff':
        return jsonify({'message': 'Only administrators or assistant administrators can register new users'}), 403

    data = request.get_json()
    required_fields = ['username', 'password', 'role']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Invalid input. Missing required fields.'}), 400

    if current_user['role'] == 'Assistant Administrator' and data['role'] != 'Security Staff':
        return jsonify({'message': 'You can only register security staff in your current role'}), 403

    # Make sure to handle optional fields gracefully
    full_name = data.get('full_name')
    email = data.get('email')
    phone_number = data.get('phone_number')

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role=data['role'],
        full_name=full_name,
        email=email,
        phone_number=phone_number
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})




@user_bp.route('/api/users', methods=['GET'])
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

@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
        return jsonify({'message': 'Only administrators or assistant administrators can delete users'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404


    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully unsubscribed to notifications!'}), 200


from sqlalchemy import and_

@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Invalid input'}), 400

    # Explicit case-sensitive username lookup
    user = User.query.filter(and_(User.username == data['username'])).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        user_info = {
            'username': user.username,
            'role': user.role,
        }
        return jsonify(access_token=access_token, user_info=user_info)
    
    return jsonify({'message': 'Invalid credentials'}), 401

@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user(user_id):
    data = request.json
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.role = data.get('role', user.role)


    db.session.commit()

    return jsonify({"message": "User updated successfully."}), 200


@user_bp.route('/api/profile', methods=['GET'])
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



@user_bp.route('/api/change-password', methods=['POST'])
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