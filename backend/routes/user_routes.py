# routes/user_routes.py
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User
from db import db
from notifications import *
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

def validate_and_format_phone_number(raw_phone_number):
    """
    Validate and format a phone number for the Philippines.

    Args:
        raw_phone_number (str): The raw phone number input.
    
    Returns:
        str: A validated and formatted E.164 phone number.
        None: If the phone number is invalid.
    """
    try:
        # Parse the phone number, assuming it is from the Philippines
        parsed_number = phonenumbers.parse(raw_phone_number, "PH")
        
        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            print(f"Invalid phone number: {raw_phone_number}")
            return None

        # Format the number in E.164 format (e.g., +639XXXXXXXXX)
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return formatted_number

    except NumberParseException as e:
        print(f"Error parsing phone number: {e}")
        return None


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
        return jsonify({'message': 'Invalid input'}), 400

    if current_user['role'] == 'Assistant Administrator' and data['role'] != 'Security Staff':
        return jsonify({'message': 'You can only register security staff in your current role'}), 403

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Validate and format the phone number
    raw_phone_number = data.get('phone_number')
    formatted_phone_number = validate_and_format_phone_number(raw_phone_number)
    if raw_phone_number and not formatted_phone_number:
        return jsonify({'message': 'Invalid phone number format'}), 400

    # Create a new user
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role=data['role'],
        full_name=data.get('full_name'),
        email=data.get('email'),
        phone_number=formatted_phone_number  # Store the formatted phone number
    )

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    # Subscribe the phone number to AWS SNS if it exists
    if formatted_phone_number:
        try:
            response = sns_client.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol='sms',
                Endpoint=formatted_phone_number
            )
            subscription_arn = response['SubscriptionArn']
            print(f"Phone number {formatted_phone_number} subscribed successfully with ARN: {subscription_arn}")

            # Save the subscription ARN in the User model
            new_user.subscription_arn = subscription_arn
            db.session.commit()  # Commit the changes to save the ARN in the database

        except Exception as e:
            print(f"Failed to subscribe phone number {formatted_phone_number} to SNS: {e}")
            return jsonify({'message': 'User registered, but failed to subscribe phone number to notifications'}), 500

    return jsonify({'message': 'User registered successfully and subscribed to notifications!'})



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

@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()

    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Update user information
    user.username = data.get('username', user.username)
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    
    # Check if phone number is being updated
    new_phone_number = data.get('phone_number', user.phone_number)
    if new_phone_number != user.phone_number:
        user.phone_number = new_phone_number
        # Update subscription (e.g., AWS SNS or any service you're using)
        update_subscription(user.subscription_arn, new_phone_number)

    user.role = data.get('role', user.role)

    db.session.commit()  # Commit changes to the database
    return jsonify({"message": "User updated successfully"}), 200


# Define the function to update the subscription
def update_subscription(subscription_arn, new_phone_number):
    # Implement your logic to update the subscription here
    # Example using AWS SNS (if your subscription is related to AWS SNS):
    import boto3

    sns = boto3.client('sns')

    # Assuming the subscription ARN is used to update the phone number
    response = sns.set_subscription_attributes(
        SubscriptionArn=subscription_arn,
        AttributeName='Endpoint',
        AttributeValue=new_phone_number  # Update with new phone number
    )

    # You can check the response and handle any errors or logging needed.
    if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
        print(f"Successfully updated subscription for ARN {subscription_arn}")
    else:
        print(f"Failed to update subscription for ARN {subscription_arn}")



@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
        return jsonify({'message': 'Only administrators or assistant administrators can delete users'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Unsubscribe from SNS if the user has a subscription ARN
    if user.subscription_arn:
        try:
            # Create an SNS client with region specification
            sns_client = boto3.client(
                'sns',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
                region_name=os.getenv("AWS_REGION")  # Specify region here
            )

            # Unsubscribe from the SNS topic
            sns_client.unsubscribe(SubscriptionArn=user.subscription_arn)
            print(f"Unsubscribed phone number {user.phone_number} from SNS successfully.")
        except Exception as e:
            print(f"Error unsubscribing: {e}")
            return jsonify({'message': 'Error unsubscribing from SNS'}), 500

    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully unsubscribed to notifications!'}), 200


@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Invalid input'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        user_info = {
            'username': user.username,
            'role': user.role,
        }
        return jsonify(access_token=access_token, user_info=user_info)
    
    return jsonify({'message': 'Invalid credentials'}), 401

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