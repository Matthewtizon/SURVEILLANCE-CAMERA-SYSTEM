# app.py
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from threading import Thread
from camera import monitor_cameras

from config import Config
from db import db, jwt
from routes.user_routes import user_bp
from routes.camera_routes import camera_bp

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS
CORS(app, origins=["http://localhost:3000"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])

bcrypt = Bcrypt(app)
db.init_app(app)
jwt.init_app(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(camera_bp)

# Other routes
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

# Function to start monitoring cameras
def start_monitoring_cameras():
    with app.app_context():
        monitor_cameras()

if __name__ == '__main__':
    try:
        thread = Thread(target=start_monitoring_cameras)
        thread.daemon = True
        thread.start()
        app.run(debug=True)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
