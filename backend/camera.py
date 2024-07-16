# camera.py
import cv2
import threading
import time
import logging
from queue import Queue
from db import db
from models import Camera

camera_queues = {}
window_name_prefix = "Camera Feed - "

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_cameras():
    detected_cameras = []
    logging.info("Starting camera detection.")
    for i in range(10):  # Adjust the range as per your available ports
        cap = cv2.VideoCapture(i)
        if cap is not None and cap.isOpened():
            detected_cameras.append(i)
            logging.info(f"Camera detected at port {i}.")
            cap.release()
        else:
            logging.info(f"No camera found at port {i}.")
    logging.info(f"Detected cameras: {detected_cameras}")
    return detected_cameras

def update_camera_db(app):
    with app.app_context():
        while True:
            detected_cameras = detect_cameras()
            existing_cameras = {camera.camera_id: camera for camera in Camera.query.all()}

            # Add new cameras to the monitoring queue
            for camera_id in detected_cameras:
                if camera_id not in camera_queues and camera_id in existing_cameras:
                    camera_queues[camera_id] = Queue()
                    camera_thread = threading.Thread(target=get_frame_from_camera, args=(camera_id,))
                    camera_thread.daemon = True
                    camera_thread.start()
                    logging.info(f"Started capturing frames from camera at port {camera_id}")

            # Remove cameras from the monitoring queue that are no longer detected
            for camera_id in list(camera_queues):
                if camera_id not in detected_cameras:
                    del camera_queues[camera_id]
                    logging.info(f"Stopped capturing frames from camera at port {camera_id}")

            logging.info("Camera monitoring update complete. Sleeping for 60 seconds.")
            time.sleep(60)

def start_monitoring(app):
    def monitor():
        with app.app_context():
            detected_cameras = detect_cameras()
            for camera_id in detected_cameras:
                if camera_id in camera_queues:
                    continue  # Skip already monitored cameras
                camera_queues[camera_id] = Queue()
                camera_thread = threading.Thread(target=get_frame_from_camera, args=(camera_id,))
                camera_thread.daemon = True
                camera_thread.start()
                logging.info(f"Started capturing frames from camera at port {camera_id}")

    monitoring_thread = threading.Thread(target=monitor)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    update_thread = threading.Thread(target=update_camera_db, args=(app,))
    update_thread.daemon = True
    update_thread.start()

def get_frame_from_camera(camera_id):
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        logging.error(f"Failed to open camera at port {camera_id}.")
        return None

    logging.info(f"Streaming frames from camera at port {camera_id}.")
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error(f"Failed to read frame from camera at port {camera_id}.")
            break
        if camera_id in camera_queues:
            camera_queues[camera_id].put(frame)

    cap.release()
    logging.info(f"Stopped streaming frames from camera at port {camera_id}.")
    cv2.destroyWindow(window_name_prefix + str(camera_id))  # Destroy window when done
    return None

def add_camera_to_queue(camera_id):
    if camera_id not in camera_queues:
        camera_queues[camera_id] = Queue()
        camera_thread = threading.Thread(target=get_frame_from_camera, args=(camera_id,))
        camera_thread.daemon = True
        camera_thread.start()
        logging.info(f"Started capturing frames from camera at port {camera_id}")
    else:
        logging.warning(f"Camera at port {camera_id} is already in the queue.")
