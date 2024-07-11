# app.py

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import logging
from threading import Thread
from models import User, Camera
from camera import monitor_cameras
from config import Config
from db import db
from socketio_instance import socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
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

    return app, socketio

def start_monitoring_cameras():
    with app.app_context():
        monitor_cameras()

def remove_duplicate_cameras():
    with app.app_context():
        cameras = Camera.query.all()
        unique_cameras = {}
        for camera in cameras:
            if camera.location not in unique_cameras:
                unique_cameras[camera.location] = camera
            else:
                db.session.delete(camera)
        db.session.commit()

if __name__ == '__main__':
    app, socketio = create_app()
    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt(app)
        if db.session.query(User).filter_by(username='yasoob').count() < 1:
            hashed_password = bcrypt.generate_password_hash('strongpassword').decode('utf-8')
            db.session.add(User(username='yasoob', password=hashed_password, role='Administrator'))
            db.session.commit()
        remove_duplicate_cameras()
    try:
        thread = Thread(target=start_monitoring_cameras)
        thread.daemon = True
        thread.start()
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
