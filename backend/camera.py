import cv2
import time
import os
import logging
from deepface import DeepFace
import numpy as np
import tensorflow as tf
import gc  # For garbage collection

logging.basicConfig(level=logging.DEBUG)

# Ensure GPU is available and set memory growth to prevent allocation errors
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print(f"Using GPU: {gpus[0]}")
    except RuntimeError as e:
        print(e)
else:
    print("No GPU found, using CPU.")

# Load SSD face detector
ssd_model = "res10_300x300_ssd_iter_140000.caffemodel"
ssd_prototxt = "deploy.prototxt"  # Ensure this file is present in your directory
face_net = cv2.dnn.readNetFromCaffe(ssd_prototxt, ssd_model)

class Camera:
    def __init__(self, dataset_path):
        # Set OpenCV to use all available CPU cores for better performance
        cv2.setNumThreads(cv2.getNumberOfCPUs())

        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        # Load the dataset for facial recognition
        self.dataset = self.load_dataset(dataset_path)

        # Ensure recordings directory exists
        if not os.path.exists('backend/recordings'):
            os.makedirs('recordings')

        # To keep track of unknown face detection
        self.last_face_status = None  # Can be 'unknown' or 'known'
        
        # Initialize tracking timestamps
        self.unknown_start_time = None  # To track when an unknown face was first detected

    def load_dataset(self, dataset_path):
        """Load the dataset images for face matching."""
        dataset = {}
        for person_folder in os.listdir(dataset_path):
            person_path = os.path.join(dataset_path, person_folder)
            if os.path.isdir(person_path):
                dataset[person_folder] = []
                for img_name in os.listdir(person_path):
                    img_path = os.path.join(person_path, img_name)
                    img = cv2.imread(img_path)
                    if img is not None:
                        dataset[person_folder].append(img)
        return dataset

    def match_face(self, face):
        """Match detected face with faces in the dataset."""
        for person_name, images in self.dataset.items():
            for ref_img in images:
                try:
                    result = DeepFace.verify(face, ref_img, model_name='VGG-Face', enforce_detection=False, detector_backend='skip')
                    if result['verified']:
                        return person_name
                except Exception as e:
                    print(f"Error during face verification: {e}")
                    continue
        return 'Unknown'

    def detect_faces_ssd(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), scalefactor=1.0, size=(300, 300), mean=(104.0, 177.0, 123.0))
        face_net.setInput(blob)
        detections = face_net.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x, y, x1, y1) = box.astype("int")
                x, y = max(0, x), max(0, y)
                x1, y1 = min(w, x1), min(h, y1)
                faces.append((x, y, x1 - x, y1 - y))
        return faces

    def get_frame(self):
        """
        Capture a frame from the camera, perform face detection and recognition, 
        and return the processed frame.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to grab frame")

        # Detect faces using SSD
        faces = self.detect_faces_ssd(frame)

        current_face_status = 'known'  # Default to 'known'

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]

            # Match the face in the dataset
            person_name = self.match_face(face)

            # Draw a rectangle around the face
            color = (0, 255, 0) if person_name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            if person_name != "Unknown":
                cv2.putText(frame, f"{person_name.upper()}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                current_face_status = 'known'
                self.unknown_start_time = None  # Reset if a known face is detected
            else:
                current_face_status = 'unknown'
                # Check if this is the first detection of an unknown face
                if self.unknown_start_time is None:
                    self.unknown_start_time = time.time()  # Start the timer
                # Removed alert triggering logic

        # Update the last face status
        self.last_face_status = current_face_status

        # Free unused memory
        gc.collect()

        return frame

    def release(self):
        """Release the camera and close any open windows."""
        self.cap.release()

# Create a singleton camera instance
camera_instance = Camera("backend/dataset")

def get_frame_from_camera():
    """Function to be used in the camera_routes.py file."""
    return camera_instance.get_frame()

def start_monitoring():
    """Function to start camera monitoring in a separate thread."""
    while True:
        try:
            frame = get_frame_from_camera()
            # Save or process frame as needed
        except Exception as e:
            logging.error(f"Camera monitoring error: {e}")
            break
    camera_instance.release()
