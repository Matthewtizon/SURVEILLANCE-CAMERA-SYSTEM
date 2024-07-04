import cv2
import time
from threading import Thread
from db import db
from models import Camera
from flask import current_app
import traceback

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location):
    while True:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame from {camera_location}. Releasing camera.")
            break
        # Add any processing for each frame if needed
        time.sleep(1)  # Add a sleep interval to reduce CPU usage
    camera.release()

# Function to detect cameras and save information to the database
def detect_cameras_and_save():
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2]
    for port in range(4):  # Increase the port range if needed
        for backend in backends:
            camera = cv2.VideoCapture(port, backend)
            if camera.isOpened():
                try:
                    camera_location = f"Camera {port+1}"
                    with current_app.app_context():
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
                    camera.release()
            else:
                backend_name = {cv2.CAP_DSHOW: "DSHOW", cv2.CAP_MSMF: "MSMF", cv2.CAP_V4L2: "V4L2"}.get(backend, backend)
                print(f"No camera detected at port {port} using backend {backend_name}.")
                camera.release()

# Function to continuously check for new cameras
def monitor_cameras(interval=60):
    try:
        while True:
            detect_cameras_and_save()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
    except Exception as e:
        print(f"Unexpected error in monitor_cameras: {e}")
        traceback.print_exc()

# If this script is run directly, start monitoring cameras
if __name__ == '__main__':
    monitor_cameras()
