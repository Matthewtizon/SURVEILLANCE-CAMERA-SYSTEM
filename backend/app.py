import shutil
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from db import db
from flask_socketio import SocketIO
from dataset import create_face_dataset
from camera import start_camera_stream, camera_streams_dict
import os
import logging
import threading
import cv2
import time
from face_recognition import recognize_faces
from alert import check_alert


# Initialize the directory for saving recordings
RECORDINGS_DIR = os.path.join(os.getcwd(), "recordings")
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Dataset directory
DATASET_DIR = os.path.join(os.getcwd(), "dataset")


# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins=["http://10.242.104.90:3000", "http://localhost", "http://10.242.104.90"])

logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": ["http://10.242.104.90:3000", "http://localhost", "http://10.242.104.90" ]}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)

    # Register user routes
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    from routes.camera_routes import create_camera_routes
    app.register_blueprint(create_camera_routes(app, socketio))

    @app.route('/api/', methods=['GET'])
    def home():
        return jsonify({'message': 'Welcome to the Flask server!'}), 200


    @app.route('/api/admin-dashboard', methods=['GET'])
    @jwt_required()
    def admin_dashboard():
        current_user = get_jwt_identity()
        if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
            return jsonify({'message': 'Unauthorized'}), 403
        return jsonify({'message': 'Welcome to the Admin Dashboard'}), 200

    @app.route('/api/security-dashboard', methods=['GET'])
    @jwt_required()
    def security_dashboard():
        current_user = get_jwt_identity()
        if current_user['role'] != 'Security Staff':
            return jsonify({'message': 'Unauthorized'}), 403
        return jsonify({'message': 'Welcome to the Security Dashboard'}), 200
    
    @app.route('/api/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    
    @app.route('/create-dataset', methods=['POST'])
    @jwt_required()
    def create_dataset():
        try:
            person_name = request.json.get('person_name')
            
            if not person_name:
                return jsonify({'message': 'Person name is required.'}), 400
            
            # Run the dataset creation in a separate thread to avoid blocking the main thread
            threading.Thread(target=create_face_dataset, args=(person_name, 500, 'dataset')).start()
            
            return jsonify({'message': f'Started creating dataset for {person_name}.'}), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
        
    @app.route('/api/dataset', methods=['GET'])
    @jwt_required()
    def get_dataset():
        try:
            dataset_content = [
                {
                    "name": name,
                    "is_directory": os.path.isdir(os.path.join(DATASET_DIR, name))
                }
                for name in os.listdir(DATASET_DIR)
            ]
            return jsonify({"success": True, "data": dataset_content}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    @app.route('/api/dataset/files/<path:filename>', methods=['GET'])
    @jwt_required()
    def get_dataset_file(filename):
        try:
            return send_from_directory(DATASET_DIR, filename)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    @app.route('/api/dataset', methods=['DELETE'])
    @jwt_required()
    def delete_dataset():
        data = request.json
        person_name = data.get('person_name')

        if not person_name:
            return jsonify({"success": False, "error": "Person name is required"}), 400

        person_path = os.path.join(DATASET_DIR, person_name)

        if not os.path.exists(person_path):
            return jsonify({"success": False, "error": "Directory does not exist"}), 404

        try:
            shutil.rmtree(person_path)
            return jsonify({"success": True, "message": f"Dataset for '{person_name}' deleted successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
    def generate_frames():
        camera = cv2.VideoCapture(0)
        while True:
            start_time = time.time()
            success, frame = camera.read()
            if not success:
                break
            else:
                recognized_faces = recognize_faces(frame)
                check_alert(recognized_faces)

                for face in recognized_faces:
                    # Ensure the tuple is unpacked correctly
                    if len(face) == 2 and isinstance(face[1], tuple) and len(face[1]) == 4:
                        person_name, (x, y, w, h) = face
                        color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, person_name.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    else:
                        print("Invalid face data:", face)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                elapsed_time = time.time() - start_time
                logging.debug(f"Frame generation time: {elapsed_time} seconds")

        
    # Route to stream video frames
    @app.route('/api/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



    return app
