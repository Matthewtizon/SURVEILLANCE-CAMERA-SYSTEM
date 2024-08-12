import cv2
import threading
import logging
import time
from collections import deque

logging.basicConfig(level=logging.INFO)

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
        retries = 0
        max_retries = 5  # Maximum number of retries if camera fails
        while self.running:
            if not self.cap.isOpened():
                logging.error(f"Camera {self.camera_id} not opened.")
                break
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frames.append(frame)
                retries = 0  # Reset retries on successful read
            else:
                retries += 1
                logging.warning(f"Camera {self.camera_id} failed to capture frame (attempt {retries}/{max_retries}).")
                if retries >= max_retries:
                    self.running = False
                    logging.error(f"Camera {self.camera_id} stopped after {max_retries} failed attempts.")
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

# Initialize single camera
camera_id = 0  # Set to the index of the single camera
camera = Camera(camera_id)

def get_frame_from_camera():
    return camera.get_frame()

def start_monitoring():
    logging.info("Started monitoring single camera.")

if __name__ == "__main__":
    start_monitoring()
    try:
        while True:
            time.sleep(1)  # Main thread stays alive to keep monitoring
    except KeyboardInterrupt:
        logging.info("Shutting down camera monitoring.")
        camera.stop()
