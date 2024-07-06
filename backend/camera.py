import cv2
import time
from threading import Thread
from queue import Queue
from db import db
from models import Camera
import traceback

# Dictionary to store queues for each camera
camera_queues = {}

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location):
    queue = Queue(maxsize=10)
    camera_queues[camera_location] = queue
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame from {camera_location}. Releasing camera.")
            break
        if not queue.full():
            queue.put(frame)
        # Uncomment the following lines to display the frame for debugging
        cv2.imshow(camera_location, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)  # Reduced sleep interval for smoother frame rate
    camera.release()
    cv2.destroyAllWindows()

# Function to detect cameras and save information to the database
def detect_cameras_and_save():
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
                        print(f"New camera detected at port {port} and information saved to the database.")
                    else:
                        print(f"Camera at port {port} already exists in the database.")
                    
                    thread = Thread(target=capture_frames, args=(camera, camera_location))
                    thread.daemon = True
                    thread.start()
                    break
                except Exception as e:
                    print(f"Error occurred with camera at port {port} using backend {backend}: {e}")
                    traceback.print_exc()
                    camera.release()
            else:
                backend_name = {cv2.CAP_DSHOW: "DSHOW"}.get(backend, backend)
                print(f"No camera detected at port {port} using backend {backend_name}.")
                camera.release()

# Function to continuously check for new cameras
def monitor_cameras(interval=60):
    while True:
        try:
            detect_cameras_and_save()
            time.sleep(interval)
        except Exception as e:
            print(f"Exception occurred in monitor_cameras thread: {e}")
            traceback.print_exc()
            time.sleep(interval)

# Run monitor_cameras on startup
if __name__ == "__main__":
    monitor_cameras()
