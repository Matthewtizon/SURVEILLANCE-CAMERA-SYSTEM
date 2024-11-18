from flask import Flask, jsonify, request, send_from_directory, abort
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import logging
from werkzeug.utils import secure_filename
from models import User, VideoDeletionAudit, Camera
from config import Config
from db import db
import cv2
from flask_socketio import SocketIO  # Import SocketIO here
import threading  # Import threading here
from face_recognition import recognize_faces
from alert import check_alert  # Import the check_alert function
import datetime
from storage import handle_detection, list_videos_in_date_range, bucket
from urllib.parse import unquote
from vidgear.gears import CamGear


# Initialize the directory for saving recordings
RECORDINGS_DIR = os.path.join(os.getcwd(), "recordings")
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)



# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins=["http://10.242.104.90:3000", "http://localhost", "http://10.242.104.90"])

logging.basicConfig(level=logging.DEBUG)


# Replace existing camera_streams with camera_streams_dict
camera_streams_dict = {}



def start_camera_stream(app, camera_id):
    with app.app_context():
        # Fetch the camera from the database by ID
        camera = Camera.query.get(camera_id)
        if not camera:
            print(f"Camera with ID {camera_id} not found.")
            return

        rtsp_url = camera.rtsp_url

        def stream():
            # Add variables to manage recording
            recording = False
            non_detected_counter = 0
            unknown_detected_time = None
            out = None
            current_recording_name = None
            frame_count = 0  # Keep track of the frames

            # Initialize CamGear for live stream with low-latency mode
            stream = CamGear(
                source=rtsp_url,
                logging=True,
                backend="FFMPEG",
                **{
                    "THREADED_QUEUE_MODE": False,
                    "time_delay": 0  # Disable any artificial delay
                }
            ).start()

            try:
                # Check if the stream is working properly by reading a frame
                frame = stream.read()
                if frame is None:
                    print(f"Failed to open camera {camera_id} with RTSP URL: {rtsp_url}")
                    return

            except Exception as e:
                print(f"Error initializing stream for camera {camera_id}: {e}")
                return


            while camera_id in camera_streams_dict:
                frame = stream.read()

                if frame is not None:
                    if frame_count % 3 == 0:  # Adjust '3' based on performance
                        # Perform face recognition
                        recognized_faces = recognize_faces(frame)
                    frame_count += 1

                    # Check if unknown faces are present
                    unknown_faces_present = any(person_name == 'unknown' for person_name, _ in recognized_faces)

                    # Logic to check if an unknown face has been detected for more than 2 seconds
                    if unknown_faces_present:
                        non_detected_counter = 0
                        if not unknown_detected_time:
                            unknown_detected_time = datetime.datetime.now()
                        else:
                            elapsed_time = (datetime.datetime.now() - unknown_detected_time).total_seconds()
                            if elapsed_time >= 2 and not recording:
                                # Start recording
                                now = datetime.datetime.now()
                                formatted_now = now.strftime("%d-%m-%y-%H-%M-%S")
                                current_recording_name = os.path.join(RECORDINGS_DIR, f'{formatted_now}.mp4')
                                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
                                out = cv2.VideoWriter(current_recording_name, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                                recording = True
                                print(f"Recording started at {formatted_now}")

                    # Stop recording if no unknown faces detected for 50 frames
                    else:
                        unknown_detected_time = None
                        non_detected_counter += 1
                        if non_detected_counter >= 50 and recording:
                            # Stop recording and release the writer
                            if out:
                                out.release()
                                handle_detection(current_recording_name)
                                out = None
                                recording = False
                                print(f"Recording stopped. Video saved: {current_recording_name}")
                            non_detected_counter = 0

                    # Write frame to the video if recording
                    if recording and out:
                        out.write(frame)

                    # Process the recognized faces to monitor for unknown faces
                    check_alert(recognized_faces)

                    for person_name, (x, y, w, h) in recognized_faces:
                        color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, person_name.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    # Display the frame using OpenCV imshow for local monitoring
                    #cv2.imshow(f"Camera {camera_id}", frame)

                    # Wait for 1 ms before continuing to next frame, and check if the 'q' key is pressed to stop
                    #if cv2.waitKey(1) & 0xFF == ord('q'):
                    #    break

                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    frame_bytes = buffer.tobytes()
                    socketio.emit('video_frame', {'camera_id': camera_id, 'frame': frame_bytes})
                else:
                    break

            stream.stop()
            if out:
                out.release()
            print(f"Camera {camera_id} released.")

        # Run the streaming process in a new thread
        threading.Thread(target=stream).start()


  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": ["http://10.242.104.90:3000", "http://localhost", "http://10.242.104.90" ]}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS", "DELETE"])
    db.init_app(app)
    jwt = JWTManager(app)

    # Register user routes
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp)

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
    
    @app.route('/api/get_recorded_videos', methods=['GET'])
    @jwt_required()
    def get_recorded_videos():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            today = datetime.datetime.now()
            start_date = today.strftime('%Y-%m-%d')  # Start of today
            end_date = today.strftime('%Y-%m-%d')    # End of today

        # Validate date formats
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

        videos = list_videos_in_date_range(start_date, end_date)
        
        if not videos:
            return jsonify({"message": "No videos found for the selected date range."}), 404

        return jsonify(videos), 200
    
    @app.route('/api/delete_video', methods=['DELETE'])
    @jwt_required()
    def delete_video():
        video_url = request.args.get('url')

        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        try:
            # Decode the URL
            decoded_url = unquote(video_url)
            
            # Extract the blob name from the decoded URL
            blob_name = decoded_url.split('/')[-1]

            # Delete the video from the bucket
            blob = bucket.blob(blob_name)
            
            # Check if the blob exists before trying to delete it
            if not blob.exists():
                return jsonify({"error": f"Video {blob_name} does not exist."}), 404

            # Delete the video
            blob.delete()
            
            # Log the deletion in the audit trail
            deleted_by = get_jwt_identity()  # Get the user identity from the JWT
            audit_entry = VideoDeletionAudit(video_name=blob_name, deleted_by=deleted_by)
            db.session.add(audit_entry)
            db.session.commit()

            return jsonify({"message": f"Video {blob_name} deleted successfully."}), 200
            
        except Exception as e:
            logging.error(f"Error deleting video: {str(e)}")
            return jsonify({"error": str(e)}), 500
        

    @app.route('/api/video_audit_trail', methods=['GET'])
    @jwt_required()  # Ensure the user is authenticated
    def get_audit_trail():
        try:
            # Query the audit trail data from the database
            audit_trails = VideoDeletionAudit.query.all()
            
            # Format the results
            audit_data = [
                {
                    "id": audit.id,
                    "video_name": audit.video_name,
                    "deleted_by": audit.deleted_by,
                    "deleted_at": audit.deleted_at.isoformat()  # Convert to ISO format
                }
                for audit in audit_trails
            ]

            return jsonify(audit_data), 200
        except Exception as e:
            logging.error(f"Error fetching audit trail: {str(e)}")
            return jsonify({"error": "Unable to fetch audit trail data."}), 500


    @app.route('/api/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    
    @app.route('/api/cameras', methods=['GET'])
    @jwt_required()
    def get_cameras():
        cameras = Camera.query.all()
        cameras_data = [
            {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "is_active": camera.is_active
            }
            for camera in cameras
        ]
        return jsonify(cameras_data), 200


    @app.route('/api/cameras', methods=['POST'])
    @jwt_required()
    def add_camera():
        data = request.get_json()

        # Create new Camera object
        new_camera = Camera(name=data['name'], rtsp_url=data['rtsp_url'], is_active=True)
        
        # Add to the database
        db.session.add(new_camera)
        db.session.commit()

        print(f"Starting thread with args: {new_camera.id}")
        thread = threading.Thread(target=start_camera_stream, args=(app, new_camera.id))
        thread.start()
        camera_streams_dict[new_camera.id] = thread

        return jsonify({"message": "Camera added and streaming started", "camera": {
            "id": new_camera.id,
            "name": new_camera.name,
            "rtsp_url": new_camera.rtsp_url,
            "is_active": new_camera.is_active
        }}), 201

    # Flask routes to update and delete cameras

    @app.route('/api/cameras/<int:camera_id>', methods=['PUT'])
    @jwt_required()
    @cross_origin(origins='http://10.242.104.90', methods=["GET", "POST", "PUT", "DELETE"])
    def update_camera(camera_id):
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({"error": "Camera not found"}), 404

        data = request.get_json()
        camera.name = data.get('name', camera.name)
        #camera.rtsp_url = data.get('rtsp_url', camera.rtsp_url)
        db.session.commit()

        return jsonify({"message": "Camera updated successfully", "camera": {
            "id": camera.id,
            "name": camera.name,
            "rtsp_url": camera.rtsp_url,
            "is_active": camera.is_active
        }}), 200

    @app.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
    @jwt_required()
    def delete_camera(camera_id):
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({"error": "Camera not found"}), 404

        # Stop the stream if the camera is active
        if camera.is_active:
            camera_streams_dict.pop(camera_id, None)  # Remove the camera stream from dictionary

        db.session.delete(camera)
        db.session.commit()
        return jsonify({"message": "Camera deleted successfully"}), 200




    return app

import signal
from gevent.pywsgi import WSGIServer
from gevent import monkey

# Declare http_server as a global variable
http_server = None

def signal_handler(signum, frame):
    logging.info("Signal received. Stopping the server...")
    http_server.stop()  # Stop the Gevent server
    exit(0)  # Exit the program

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

        # Automatically start active cameras
        active_cameras = Camera.query.filter_by(is_active=True).all()
        for camera in active_cameras:
            if camera.id not in camera_streams_dict:
                thread = threading.Thread(target=start_camera_stream, args=(app, camera.id))
                thread.start()
                camera_streams_dict[camera.id] = thread

    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        http_server = WSGIServer(('0.0.0.0', 5000), app)
        logging.info("Server is running on http://0.0.0.0:5000")
        http_server.serve_forever()
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")


if __name__ == '__main__':
    initialize()

