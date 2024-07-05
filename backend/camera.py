# backend/camera.py
import cv2
import time
from threading import Thread
from db import db
from models import Camera
from flask import current_app, Response
import traceback

# Function to continuously capture frames from a camera
def capture_frames(camera, camera_location):
    while True:
        ret, frame = camera.read()
        if not ret:
            print(f"Failed to grab frame from {camera_location}. Releasing camera.")
            break
        # Here you can save the frame to be streamed or processed further
        # Example: cv2.imshow(camera_location, frame) - To display the frame
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
                backend_name = {cv2.CAP_DSHOW: "DSHOW", cv2.CAP_MSMF: "MSMF", cv2.CAP_V4L2: "V4L2"}.get(backend, backend)
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

# Function to generate camera feed
def generate_camera_feed(camera_id):
    with current_app.app_context():
        camera = Camera.query.get(camera_id)
        if camera is None:
            return Response("Camera not found", status=404)

        # Example logic to capture frames (replace with your actual camera handling)
        def generate():
            capture = cv2.VideoCapture(camera.url)  # Example: camera.url should be the URL or identifier for the camera
            while True:
                ret, frame = capture.read()
                if not ret:
                    break
                # Convert frame to JPEG format
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    break
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            capture.release()

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')