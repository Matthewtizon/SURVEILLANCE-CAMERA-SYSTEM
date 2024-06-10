from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS 



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:johnmatthew300@localhost:3306/surveillance_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

CORS(app, origins=["http://localhost:3000"])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(username='johnmatthew').count() < 1:
        hashed_password = bcrypt.generate_password_hash('johnmatthew300').decode('utf-8')
        db.session.add(User(
            username='johnmatthew',
            password=hashed_password,
            role='Security Staff'
        ))
        db.session.commit()


@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Administrator':
        return jsonify({'message': 'Only administrators can register new users'}), 403

    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Received data:", data)  # Debugging statement
    user = User.query.filter_by(username=data['username']).first()
    if user:
        print("User found:", user.username)  # Debugging statement
        if bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity={'username': user.username, 'role': user.role})
            user_info = {
                'username': user.username,
                'role': user.role,
            }
            print("Authentication successful")  # Debugging statement
            return jsonify(access_token=access_token, user_info=user_info)
        else:
            print("Password does not match")  # Debugging statement
    else:
        print("User not found")  # Debugging statement
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/admin-dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Administrator':
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify({'message': 'Welcome to the Admin Dashboard'}), 200

@app.route('/security-dashboard', methods=['GET'])
@jwt_required()
def security_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Security Staff':
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify({'message': 'Welcome to the Security Dashboard'}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(debug=True)