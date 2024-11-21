import cv2
import os
import numpy as np
from deepface import DeepFace
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
from ultralytics import YOLO  # For YOLOv8
import datetime
import pandas as pd
from PIL import Image
import logging
import time
from alert import check_alert, start_alert_thread  # Import the check_alert function from alert.py

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

# Load YOLOv8 model for face detection
yolo_model = YOLO("yolov8n_100e.pt")  # Pre-trained YOLOv8-Tiny for face detection

# Path to dataset
dataset_path = 'dataset'


import os
logging.debug(f"Dataset exists: {os.path.exists(dataset_path)}")
logging.debug(f"Dataset path: {dataset_path}")


def create_face_database(dataset_path):
    face_db = []
    for person_folder in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_folder)
        if os.path.isdir(person_path):
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                try:
                    # Validate image format
                    with Image.open(img_path) as img:
                        img.verify()
                    face_db.append({"person": person_folder, "img_path": img_path})
                except Exception as e:
                    print(f"Skipping invalid image {img_path}: {e}")
    # Save to a DataFrame for compatibility with DeepFace's find method
    return pd.DataFrame(face_db)


face_database = create_face_database(dataset_path)


def match_face(face):
    logging.debug(f"Matching face with shape: {face.shape if face is not None else 'None'}")
    
    # Perform face matching using DeepFace
    results = DeepFace.find(face, db_path=dataset_path, model_name="VGG-Face", distance_metric="cosine", enforce_detection=False)


    # Check if results is a list and it contains the correct structure
    if isinstance(results, list) and len(results) > 0:
        # The first element of the list contains a DataFrame of the results
        df_results = results[0]  # Assuming the list contains a single DataFrame
        if isinstance(df_results, pd.DataFrame) and not df_results.empty:
            best_match = df_results.iloc[0]  # Access the first match
            # Adjust threshold to control how similar the faces should be to match
            if best_match['distance'] < 0.5:  # Example: If distance < 0.6, it's a match
                label = os.path.basename(os.path.dirname(best_match['identity']))
            else:
                label = "Unknown"
        else:
            label = "Unknown"
    else:
        label = "Unknown"

    return label


# Detect faces using YOLOv8
def detect_faces_yolo(frame):
    # Perform YOLOv8 inference
    results = yolo_model.predict(frame, conf=0.5)  # Confidence threshold at 50%
    detections = results[0].boxes  # Get bounding boxes

    faces = []
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])  # Extract bounding box coordinates
        faces.append((x1, y1, x2 - x1, y2 - y1))  # Convert to (x, y, w, h) format
    return faces

def recognize_faces(frame):
    faces = detect_faces_yolo(frame)  # Use YOLOv8 for face detection
    results = []
    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        person_name = match_face(face)

        # Add this line to debug detected faces
        print(f"Detected: {person_name}")
        
        results.append((person_name, (x, y, w, h)))
    
    # Call alert checker in a separate thread and pass the faces detected
    start_alert_thread(faces)  # Start alert check thread

    return results

