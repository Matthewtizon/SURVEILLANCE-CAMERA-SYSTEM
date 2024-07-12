from queue import Queue
import cv2
import time
from threading import Thread, Lock
from db import db
from models import Camera
import logging
from sqlalchemy.orm import scoped_session, sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a scoped session for SQLAlchemy
Session = scoped_session(sessionmaker())

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location, queue, frame_lock):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.error(f"Failed to grab frame from {camera_location}. Releasing camera.")
                break
            if not queue.full():
                with frame_lock:
                    queue.put(frame.copy())  # Make a copy to avoid modifying the original frame
                    # Example of saving to database without Flask context
                    save_frame_to_db(frame, camera_location)
            # Uncomment the following lines to display the frame for debugging
            cv2.imshow(camera_location, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.1)  # Adjust sleep interval for frame rate
    finally:
        camera.release()
        logger.info(f"Camera release completed for {camera_location}")
        cv2.destroyAllWindows()

# Function to save frame to database
def save_frame_to_db(frame, location):
    session = Session()
    try:
        # Example: Save frame data to database
        # Ensure proper model and table setup in models.py
        # Example:
        new_frame = CameraFrame(location=location, frame_data=frame.tobytes())
        session.add(new_frame)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving frame to database: {e}")
        session.rollback()
    finally:
        session.close()

# Function to detect cameras and save information to the database
def detect_cameras_and_save():
    backends = [cv2.CAP_DSHOW]  # Example: Use only DSHOW backend
    for port in range(4):  # Example: Increase port range if needed
        for backend in backends:
            camera = cv2.VideoCapture(port, backend)
            if camera.isOpened():
                try:
                    camera_location = f"Camera {port+1}"
                    existing_camera = Session().query(Camera).filter_by(location=camera_location).first()
                    if existing_camera is None:
                        new_camera = Camera(location=camera_location)
                        Session().add(new_camera)
                        Session().commit()
                        logger.info(f"New camera detected at port {port} and information saved to the database.")
                    else:
                        logger.info(f"Camera at port {port} already exists in the database.")

                    # Start capturing frames in a thread
                    queue = Queue(maxsize=1)  # Adjust queue size as needed
                    frame_lock = Lock()
                    thread = Thread(target=capture_frames, args=(camera, camera_location, queue, frame_lock))
                    thread.daemon = True
                    thread.start()

                except Exception as e:
                    logger.error(f"Error occurred with camera at port {port} using backend {backend}: {e}")
                    camera.release()
            else:
                backend_name = {cv2.CAP_DSHOW: "DSHOW"}.get(backend, backend)
                logger.warning(f"No camera detected at port {port} using backend {backend_name}.")
                camera.release()

# Function to continuously monitor cameras
def monitor_cameras():
    try:
        while True:
            detect_cameras_and_save()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting camera monitoring.")
    except Exception as e:
        logger.error(f"Exception occurred in monitor_cameras thread: {e}")
    finally:
        # Cleanup session resources
        Session.remove()

def start_camera_monitoring():
    monitor_cameras()

