import cv2
import time
import os
import logging
import gc
import base64
from io import BytesIO
from tasks import process_frame

logging.basicConfig(level=logging.DEBUG)

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

    def get_frame(self):
        """Capture a frame from the camera, encode it, and send it to the Celery worker."""
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to grab frame")

        # Encode the frame as a JPEG image
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise Exception("Failed to encode frame")

        # Convert to base64 to make it JSON serializable
        frame_encoded = base64.b64encode(buffer).decode('utf-8')

        # Send encoded frame to the background Celery task for face recognition
        task = process_frame.delay(frame_encoded)  # Call the Celery task asynchronously

        return frame

    def release(self):
        """Release the camera."""
        self.cap.release()

camera_instance = Camera()

def get_frame_from_camera():
    """Function to be used in the camera_routes.py file."""
    return camera_instance.get_frame()

def start_monitoring():
    """Function to start camera monitoring."""
    while True:
        try:
            frame = get_frame_from_camera()
            # Display the frame in a window
            cv2.imshow('Camera Feed', frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            logging.error(f"Camera monitoring error: {e}")
            break

    camera_instance.release()
    cv2.destroyAllWindows()  # Close the OpenCV window

