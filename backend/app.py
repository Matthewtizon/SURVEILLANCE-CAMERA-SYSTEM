from flask import Flask, jsonify, request, send_from_directory, abort
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import logging
from werkzeug.utils import secure_filename
from models import User
from config import Config
from db import db
import cv2
from flask_socketio import SocketIO  # Import SocketIO here
import threading  # Import threading here
from face_recognition import recognize_faces
from alert import check_alert  # Import the check_alert function



# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="http://localhost:3000")

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)

    # Register user routes
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    @app.route('/admin-dashboard', methods=['GET'])
    @jwt_required()
    def admin_dashboard():
        current_user = get_jwt_identity()
        if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
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

    # Camera streaming routes
    camera_streams = {}

    def start_camera(camera_ip):
        cap = cv2.VideoCapture(int(camera_ip))
        if not cap.isOpened():
            print(f"Failed to open camera {camera_ip}")
            return

        while camera_ip in camera_streams:
            ret, frame = cap.read()
            if ret:
                # Perform face recognition
                recognized_faces = recognize_faces(frame)

                # Process the recognized faces to monitor for unknown faces
                check_alert(recognized_faces)

                for person_name, (x, y, w, h) in recognized_faces:
                    color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, person_name.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                frame_bytes = buffer.tobytes()
                socketio.emit('video_frame', {'camera_ip': camera_ip, 'frame': frame_bytes})
            else:
                break

        cap.release()

    @app.route('/open_camera/<camera_ip>', methods=['GET'])
    @jwt_required()
    def open_camera(camera_ip):
        if camera_ip not in camera_streams:
            thread = threading.Thread(target=start_camera, args=(camera_ip,))
            thread.start()
            camera_streams[camera_ip] = thread
            return jsonify({'message': f'Camera {camera_ip} started'}), 200
        return jsonify({'message': f'Camera {camera_ip} is already running'}), 400

    @app.route('/close_camera/<camera_ip>', methods=['GET'])
    @jwt_required()
    def close_camera(camera_ip):
        if camera_ip in camera_streams:
            del camera_streams[camera_ip]
            return jsonify({'message': f'Camera {camera_ip} stopped'}), 200
        return jsonify({'message': f'Camera {camera_ip} is not running'}), 400

    return app

def initialize():
    app = create_app()
    socketio.init_app(app)

    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt(app)

        if db.session.query(User).filter_by(username='yasoob').count() < 1:
            hashed_password = bcrypt.generate_password_hash('strongpassword').decode('utf-8')
            new_user = User(
                username='yasoob',
                password=hashed_password,
                role='Administrator',
                full_name='Yasoob Ali',
                email='yasoob@example.com',
                phone_number='123-456-7890'
            )
            db.session.add(new_user)
            db.session.commit()

    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

if __name__ == '__main__':
    initialize()
