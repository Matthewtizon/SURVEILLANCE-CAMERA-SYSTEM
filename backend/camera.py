import cv2
import time
from threading import Thread
from queue import Queue
from db import db
from models import Camera
from flask import current_app as app
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store queues for each camera
camera_queues = {}

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location, queue):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.error(f"Failed to grab frame from {camera_location}. Releasing camera.")
                break
            if not queue.full():
                queue.put(frame)
            # Uncomment the following lines to display the frame for debugging
            #cv2.imshow(camera_location, frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #   break
            time.sleep(0.1)  # Reduced sleep interval for smoother frame rate
    finally:
        camera.release()
        logger.info(f"Camera release completed for {camera_location}")
        #cv2.destroyAllWindows()

# Function to detect cameras and save information to the database
def detect_cameras_and_save():
    with app.app_context():  # Ensure the application context is available
        backends = [cv2.CAP_DSHOW]  # Use only DSHOW backend
        for port in range(4):  # Increase the port range if needed
            for backend in backends:
                camera = cv2.VideoCapture(port, backend)
                if camera.isOpened():
                    try:
                        camera_location = f"Camera {port+1}"
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

                        thread = Thread(target=capture_frames, args=(camera, camera_location, queue))
                        thread.daemon = True
                        thread.start()
                        break
                    except Exception as e:
                        logger.error(f"Error occurred with camera at port {port} using backend {backend}: {e}")
                        traceback.print_exc()
                        camera.release()
                else:
                    backend_name = {cv2.CAP_DSHOW: "DSHOW"}.get(backend, backend)
                    logger.warning(f"No camera detected at port {port} using backend {backend_name}.")
                    camera.release()

# Function to continuously check for new cameras
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
    finally:
        # Add cleanup code here if necessary
        pass

def start_monitoring():
    # Import the Flask app instance and push its context
    from app import create_app
    
    # Ensure to correctly obtain the Flask app instance
    flask_app, _ = create_app()  # Assuming create_app returns (app, socketio)

    with flask_app.app_context():
        monitor_cameras()

if __name__ == '__main__':
    start_monitoring()
