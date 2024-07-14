import time
import cv2
import logging
from threading import Thread, Lock
from queue import Queue
import traceback
from db import db
from models import Camera
from flask import current_app as app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

camera_queues = {}
frame_data = {}
thread_lock = Lock()

def get_frame_from_camera(camera_id):
    with thread_lock:
        return frame_data.get(camera_id)

def update_frame_data(camera_id, frame):
    with thread_lock:
        frame_data[camera_id] = frame

def capture_frames(camera, camera_id, queue):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.error(f"Failed to grab frame from camera {camera_id}. Releasing camera.")
                break
            if not queue.full():
                queue.put(frame)
<<<<<<< HEAD
                update_frame_data(camera_location, frame.copy())  # Store a copy of the frame
                logger.info(f"Captured frame for {camera_location}")  # Debug statement
            # Uncomment the following line to display the frame for debugging
            cv2.imshow(camera_location, frame)  # Commented out to prevent multiple displays
=======
                update_frame_data(camera_id, frame.copy())
                logger.info(f"Captured frame for camera {camera_id}")
>>>>>>> new1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Remove the sleep interval to allow continuous frame capturing
            # time.sleep(0.1)
    finally:
        camera.release()
        logger.info(f"Camera release completed for camera {camera_id}")
        cv2.destroyAllWindows()
        if camera_id in camera_queues:
            del camera_queues[camera_id]
        with thread_lock:
            if camera_id in frame_data:
                del frame_data[camera_id]

def detect_cameras_and_save():
    with app.app_context():
        backends = [cv2.CAP_DSHOW]
        for port in range(4):
            for backend in backends:
                camera = cv2.VideoCapture(port, backend)
                if camera.isOpened():
                    try:
                        camera_id = port + 1
                        existing_camera = Camera.query.filter_by(camera_id=camera_id).first()
                        if existing_camera is None:
                            new_camera = Camera(camera_id=camera_id, location=f"Camera {camera_id}")
                            db.session.add(new_camera)
                            db.session.commit()
                            logger.info(f"New camera detected at port {port} and information saved to the database.")
                        else:
                            logger.info(f"Camera at port {port} already exists in the database.")
                        
                        queue = Queue(maxsize=10)
                        camera_queues[camera_id] = queue

                        thread = Thread(target=capture_frames, args=(camera, camera_id, queue))
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

def monitor_cameras(interval=60):
    try:
        while True:
            with app.app_context():
                detect_cameras_and_save()
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting camera monitoring.")
    except Exception as e:
        logger.error(f"Exception occurred in monitor_cameras thread: {e}")
        traceback.print_exc()

def start_monitoring():
    from app import create_app
    flask_app = create_app()
    with flask_app.app_context():
        monitor_cameras()
