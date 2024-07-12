from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import logging
from threading import Thread
from db import db
from models import User, Camera
from config import Config
from socketio_instance import socketio
from camera import start_camera_monitoring

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)

    # Setup CORS
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    # Register Blueprints
    from routes.user_routes import user_bp
    from routes.camera_routes import camera_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(camera_bp, url_prefix='/api')  # Ensure correct prefix

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

    return app

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt(app)
        # Create a default admin user if not exists
        if db.session.query(User).filter_by(username='yasoob').count() < 1:
            hashed_password = bcrypt.generate_password_hash('strongpassword').decode('utf-8')
            db.session.add(User(
                username='yasoob',
                password=hashed_password,
                role='Administrator'
            ))
            db.session.commit()

        # Start camera monitoring in a separate thread
        thread = Thread(target=start_camera_monitoring)
        thread.daemon = True
        thread.start()

    try:
        # Initialize socketio with the app
        socketio.init_app(app)

        socketio.run(app, debug=True)  # Use socketio.run instead of app.run for SocketIO
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
