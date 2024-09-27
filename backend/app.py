from flask import Flask, jsonify, request, send_from_directory, abort
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import logging
import threading
from camera import start_monitoring
from config import Config
from db import db
from models import User  # Ensure to import the User model
from tasks import process_frame  # Import the Celery task
from celery.result import AsyncResult  # To track the Celery task result
import redis

UPLOAD_FOLDER = 'dataset'  # Update this path to your dataset folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)
    
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    from routes.camera_routes import camera_bp
    app.register_blueprint(camera_bp)

    # Create a connection to the Redis server
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    # Test the connection
    try:
        redis_client.ping()
        logging.info("Connected to Redis successfully!")
    except redis.ConnectionError:
        logging.error("Could not connect to Redis.")

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

    @app.route('/upload_image/<person_name>', methods=['POST'])
    @jwt_required()
    def upload_image(person_name):
        current_user = get_jwt_identity()
        if current_user['role'] not in ['Administrator', 'Assistant Administrator']:
            return jsonify({'message': 'Unauthorized'}), 403
        
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Save the file in the dataset/person_name/ directory
            person_folder = os.path.join(app.config['UPLOAD_FOLDER'], person_name)
            if not os.path.exists(person_folder):
                os.makedirs(person_folder)

            file.save(os.path.join(person_folder, filename))
            return jsonify({'success': True, 'filename': filename}), 200
        
        return jsonify({'error': 'File upload failed'}), 500
    
    @app.route('/images', methods=['GET'])
    def list_images():
        images = {}
        dataset_directory = os.path.join(app.root_path, 'dataset')
        
        for person in os.listdir(dataset_directory):
            person_folder = os.path.join(dataset_directory, person)
            if os.path.isdir(person_folder):
                images[person] = os.listdir(person_folder)
        
        return jsonify(images)

    @app.route('/images/<filename>')
    @jwt_required()  # Ensure the user is logged in
    def get_image(filename):
        current_user = get_jwt_identity()
        
        # Define roles that are allowed to view images
        allowed_roles = ['Administrator', 'Assistant Administrator', 'Security Staff']

        # Check if the user has the required role to access the image
        if current_user['role'] not in allowed_roles:
            return abort(403)  # Forbidden

        # Ensure the filename is safe to prevent directory traversal attacks
        if '..' in filename or filename.startswith('/'):
            return abort(400)  # Bad request

        # Define the path to the images directory
        images_directory = os.path.join(app.root_path, 'images')
        
        # Check if the file exists
        if not os.path.isfile(os.path.join(images_directory, filename)):
            return abort(404)  # File not found
        
        # Serve the image file if everything is valid
        return send_from_directory(images_directory, filename)
    
    @app.route('/recognize-face', methods=['POST'])
    @jwt_required()
    def recognize_face():
        current_user = get_jwt_identity()

        # Check if the user has the correct role to perform face recognition
        if current_user['role'] not in ['Administrator', 'Security Staff']:
            return jsonify({'message': 'Unauthorized'}), 403

        # Get the frame from the request (in this example, assuming the frame is sent as a file)
        if 'frame' not in request.files:
            return jsonify({'error': 'No frame provided'}), 400

        file = request.files['frame']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            frame_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(frame_path)

            # Send the frame to Celery for processing
            task = process_frame.delay(frame_path)

            # Return the task ID to the client
            return jsonify({'task_id': task.id}), 202
        else:
            return jsonify({'error': 'Invalid file format'}), 400

    # Unified task status endpoint
    @app.route('/task-status/<task_id>', methods=['GET'])
    @jwt_required()
    def get_task_status(task_id):
        current_user = get_jwt_identity()

        # Check if the user has the correct role to view task status
        if current_user['role'] not in ['Administrator', 'Security Staff']:
            return jsonify({'message': 'Unauthorized'}), 403

        # Retrieve task information using Celery's AsyncResult
        task_result = AsyncResult(task_id)

        if task_result.state == 'PENDING':
            response = {
                'state': task_result.state,
                'status': 'Pending...'
            }
        elif task_result.state != 'FAILURE':
            response = {
                'state': task_result.state,
                'status': task_result.info.get('status', ''),
                'result': task_result.result  # You can also return the result if needed
            }
        else:
            # Something went wrong with the task
            response = {
                'state': task_result.state,
                'status': str(task_result.info),  # Error message from task
            }
        
        return jsonify(response)

    return app

def start_camera_monitoring():
    """Ensure that only one camera monitoring thread is started."""
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
