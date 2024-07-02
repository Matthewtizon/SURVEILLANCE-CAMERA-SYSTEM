import cv2
import time
from threading import Thread
from db import db
from models import Camera

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location):
    while True:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame from {camera_location}")
            break
        # Add any processing for each frame if needed
        # Example: Save frame to file or analyze frame
        # For now, just continue to capture frames
        time.sleep(1)  # Add a sleep interval to reduce CPU usage
    camera.release()

# Function to detect cameras and save information to the database
def detect_cameras_and_save():
    for port in range(4):  # Assuming there are 4 ports, you can adjust as needed
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            # Camera detected, retrieve information
            camera_location = f"Camera {port+1}"
            # Check if the camera is already in the database
            existing_camera = Camera.query.filter_by(location=camera_location).first()
            if existing_camera is None:
                # Save camera information to the database
                new_camera = Camera(location=camera_location)
                db.session.add(new_camera)
                db.session.commit()
                print(f"New camera detected at port {port} and information saved to the database.")
            else:
                print(f"Camera at port {port} already exists in the database.")
            
            # Start a new thread to capture frames from this camera
            thread = Thread(target=capture_frames, args=(camera, camera_location))
            thread.daemon = True
            thread.start()
        else:
            print(f"No camera detected at port {port}.")

# Function to continuously check for new cameras
def monitor_cameras(interval=60):
    while True:
        detect_cameras_and_save()
        time.sleep(interval)

# To start monitoring cameras
if __name__ == "__main__":
    monitor_cameras()
