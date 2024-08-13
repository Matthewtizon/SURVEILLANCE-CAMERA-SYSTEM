from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import logging
import threading  # Import threading module
from models import User
from camera import start_monitoring
from config import Config
from db import db

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)
    
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    from routes.camera_routes import camera_bp
    app.register_blueprint(camera_bp)

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

    return app

def start_camera_monitoring():
    # Ensure that only one camera monitoring thread is started
    if not any(t.name == "CameraMonitor" and t.is_alive() for t in threading.enumerate()):
        monitor_thread = threading.Thread(target=start_monitoring, name="CameraMonitor")
        monitor_thread.daemon = True
        monitor_thread.start()
        logging.info("Started camera monitoring.")
    else:
        logging.info("Camera monitoring is already running.")

def initialize():
    app = create_app()

    with app.app_context():
        db.create_all()
        bcrypt = Bcrypt(app)

        # Check if the user does not exist
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

    start_camera_monitoring()

    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping Flask application.")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

if __name__ == '__main__':
    initialize()