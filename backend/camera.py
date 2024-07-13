import cv2
import time
from threading import Thread, Lock
from queue import Queue
import logging
import traceback
import base64
from db import db
from models import Camera
from flask import current_app as app
from socketio_instance import socketio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store camera queues and frame data
camera_queues = {}
frame_data = {}

# Lock for thread-safe operations
thread_lock = Lock()

def emit_camera_frames(camera_location):
    global frame_data
    while True:
        with thread_lock:
            if camera_location in frame_data:
                frame = frame_data[camera_location]
                # Encode frame to JPEG bytes and then base64
                frame_data_encoded = cv2.imencode('.jpg', frame)[1].tobytes()
                frame_base64 = base64.b64encode(frame_data_encoded).decode('utf-8')
                socketio.emit('camera_frame', {'frame': frame_base64}, namespace='/')  # Ensure correct namespace
        socketio.sleep(0.1)  # Adjust the sleep interval as needed for your frame rate

def start_frame_thread(camera_location):
    if camera_location not in camera_queues:
        # Start only if not already started
        thread = socketio.start_background_task(target=emit_camera_frames, camera_location=camera_location)
        return thread

def update_frame_data(camera_location, frame):
    with thread_lock:
        frame_data[camera_location] = frame

def capture_frames(camera, camera_location, queue):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.error(f"Failed to grab frame from {camera_location}. Releasing camera.")
                break
            if not queue.full():
                queue.put(frame)
                update_frame_data(camera_location, frame.copy())  # Store a copy of the frame
                logger.info(f"Captured frame for {camera_location}")  # Debug statement
            # Uncomment the following line to display the frame for debugging
            cv2.imshow(camera_location, frame)  # Commented out to prevent multiple displays

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)  # Reduced sleep interval for smoother frame rate

    finally:
        camera.release()
        logger.info(f"Camera release completed for {camera_location}")
        cv2.destroyAllWindows()
        # Remove camera from queues and frame data after release
        if camera_location in camera_queues:
            del camera_queues[camera_location]
        with thread_lock:
            if camera_location in frame_data:
                del frame_data[camera_location]

# Function to detect cameras and save them in the database
def detect_cameras_and_save():
    with app.app_context():  # Ensure the application context is available
        backends = [cv2.CAP_DSHOW]  # Use only DSHOW backend
        for port in range(4):  # Increase the port range if needed
            for backend in backends:
                camera = cv2.VideoCapture(port, backend)
                if camera.isOpened():
                    try:
                        camera_location = f"Camera {port + 1} - {port * 700}"
                        existing_camera = Camera.query.filter_by(location=camera_location).first()
                        if existing_camera is None:
                            new_camera = Camera(location=camera_location)
                            db.session.add(new_camera)
                            db.session.commit()
                            logger.info(f"New camera detected at port {port} and information saved to the database.")
                        else:
                            logger.info(f"Camera at port {port} already exists in the database.")
                        
                        queue = Queue(maxsize=10)
                        camera_queues[camera_location] = queue

                        # Start a separate thread to capture frames
                        thread = Thread(target=capture_frames, args=(camera, camera_location, queue))
                        thread.daemon = True
                        thread.start()

                        # Start a thread to emit frames via SocketIO
                        start_frame_thread(camera_location)
                        
                        break
                    except Exception as e:
                        logger.error(f"Error occurred with camera at port {port} using backend {backend}: {e}")
                        traceback.print_exc()
                        camera.release()
                else:
                    backend_name = {cv2.CAP_DSHOW: "DSHOW"}.get(backend, backend)
                    logger.warning(f"No camera detected at port {port} using backend {backend_name}.")
                    camera.release()

# Function to continuously monitor cameras
def monitor_cameras(interval=60):
    try:
        while True:
            with app.app_context():  # Ensure the application context is available
                detect_cameras_and_save()
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting camera monitoring.")
    except Exception as e:
        logger.error(f"Exception occurred in monitor_cameras thread: {e}")
        traceback.print_exc()

# Function to start monitoring cameras
def start_monitoring():
    from app import create_app
    
    flask_app, _ = create_app()  # Assuming create_app returns (app, socketio)
    
    with flask_app.app_context():
        monitor_cameras()
