from flask import Flask, jsonify, request, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from flask_cors import CORS
import cv2
import imutils

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:johnmatthew300@localhost:3306/surveillance_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

# Configure CORS
CORS(app, origins=["http://localhost:3000"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models and database setup
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Camera(db.Model):
    camera_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(username='yasoob').count() < 1:
        hashed_password = bcrypt.generate_password_hash('strongpassword').decode('utf-8')
        db.session.add(User(
            username='yasoob',
            password=hashed_password,
            role='Administrator'
        ))
        db.session.commit()

# Routes
@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Administrator':
        return jsonify({'message': 'Only administrators can register new users'}), 403

    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return jsonify({'message': 'Invalid input'}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Administrator':
        return jsonify({'message': 'Unauthorized'}), 403
    
    users = User.query.all()
    user_list = [{"user_id": user.user_id, "username": user.username, "role": user.role} for user in users]
    return jsonify(user_list), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'Administrator':
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/login', methods=['POST'])
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

@app.route('/camera_feed/<int:camera_id>')
def camera_feed(camera_id):
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded_token = decode_token(token)
        current_user = decoded_token['sub']
    except Exception as e:
        return jsonify({'message': 'Token is invalid or expired'}), 401

    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    @stream_with_context
    def generate():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error opening video stream or file"

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = imutils.resize(frame, width=400)  # Adjust frame size if needed
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = Camera.query.all()
    camera_list = [{"camera_id": camera.camera_id, "location": camera.location} for camera in cameras]
    return jsonify(camera_list), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(debug=True)
