# app.py
from flask import Flask, Response, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import logging
from threading import Thread
from models import User, Camera
from camera import start_monitoring, camera_queues, get_frame_from_camera, add_camera_to_queue
from config import Config
from db import db
import cv2

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)
    logging.basicConfig(level=logging.DEBUG)
    from routes.user_routes import user_bp
    from routes.camera_routes import camera_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(camera_bp)

    @app.route('/admin-dashboard', methods=['GET'])
    @jwt_required()
    def admin_dashboard():
        current_user = get_jwt_identity()
        if (current_user['role'] != 'Administrator'):
            return jsonify({'message': 'Unauthorized'}), 403
        return jsonify({'message': 'Welcome to the Admin Dashboard'}), 200

    @app.route('/security-dashboard', methods=['GET'])
    @jwt_required()
    def security_dashboard():
        current_user = get_jwt_identity()
        if (current_user['role'] != 'Security Staff'):
            return jsonify({'message': 'Unauthorized'}), 403
        return jsonify({'message': 'Welcome to the Security Dashboard'}), 200

    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    @app.route('/cameras', methods=['GET'])
    @jwt_required()
    def get_cameras():
        try:
            cameras = Camera.query.all()
            serialized_cameras = [camera.serialize() for camera in cameras]
            return jsonify(cameras=serialized_cameras), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route('/start_camera_streams', methods=['GET'])
    @jwt_required()
    def start_camera_streams():
        try:
            for camera in Camera.query.filter_by(active=True).all():
                add_camera_to_queue(camera.camera_id)
            return jsonify(message='Started camera streams successfully'), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route('/video_feed/<int:camera_id>', methods=['GET'])
    def video_feed(camera_id):
        if camera_id not in camera_queues:
            return jsonify({"error": "Camera not found"}), 404
        return Response(gen_frames(camera_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


    return app

def gen_frames(camera_id):
    while True:
        frame = camera_queues[camera_id].get()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break

def initialize():
    app = create_app()

    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt(app)

        if db.session.query(User).filter_by(username='yasoob').count() < 1:
            hashed_password = bcrypt.generate_password_hash('strongpassword').decode('utf-8')
            db.session.add(User(username='yasoob', password=hashed_password, role='Administrator'))
            db.session.commit()

        start_monitoring(app)

    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == '__main__':
    initialize()
