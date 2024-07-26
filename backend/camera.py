import cv2
import threading
import logging
import time
from collections import deque

logging.basicConfig(level=logging.INFO)

camera_queues = {}
max_ports = 4  # Define the maximum number of ports to check

class Camera:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        self.frames = deque(maxlen=10)
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()
        logging.info(f"Camera {camera_id} initialized and streaming started.")

    def update_frames(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frames.append(frame)
            else:
                logging.warning(f"Camera {self.camera_id} failed to capture frame.")
                time.sleep(1)  # Wait before retrying

    def get_frame(self):
        with self.lock:
            if self.frames:
                return self.frames[-1]
            return None

    def stop(self):
        self.running = False
        self.cap.release()
        logging.info(f"Camera {self.camera_id} stopped streaming.")

def detect_cameras():
    cameras = []
    for i in range(max_ports):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
            logging.info(f"Camera detected at port {i}.")
        else:
            logging.info(f"No camera detected at port {i}.")
    return cameras

def initialize_cameras():
    camera_ids = detect_cameras()
    for camera_id in camera_ids:
        if camera_id not in camera_queues:
            camera_queues[camera_id] = Camera(camera_id)
        else:
            logging.info(f"Camera {camera_id} already initialized.")

def get_frame_from_camera(camera_id):
    if camera_id in camera_queues:
        return camera_queues[camera_id].get_frame()
    return None

def monitor_cameras():
    while True:
        current_cameras = set(camera_queues.keys())
        detected_cameras = set(detect_cameras())

        # Add new cameras
        new_cameras = detected_cameras - current_cameras
        for camera_id in new_cameras:
            camera_queues[camera_id] = Camera(camera_id)

        # Remove disconnected cameras
        removed_cameras = current_cameras - detected_cameras
        for camera_id in removed_cameras:
            camera_queues[camera_id].stop()
            del camera_queues[camera_id]

        time.sleep(60)  # Check for new/removed cameras every 60 seconds

def start_monitoring():
    initialize_cameras()
    monitor_thread = threading.Thread(target=monitor_cameras, daemon=True)
    monitor_thread.start()
    logging.info("Started camera monitoring.")