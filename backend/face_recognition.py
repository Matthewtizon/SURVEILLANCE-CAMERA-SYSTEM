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

# Path to save recordings
RECORDINGS_DIR = 'recordings'
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Variables for recording logic
unknown_detected_time = None
recording = False
non_detected_counter = 0
out = None
current_recording_name = None

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
    try:
        # Perform face matching using DeepFace
        results = DeepFace.find(face, db_path=dataset_path, model_name="VGG-Face", distance_metric="cosine", enforce_detection=False)
        if isinstance(results, list) and len(results) > 0:
            df_results = results[0]  # The first element contains a DataFrame
            if isinstance(df_results, pd.DataFrame) and not df_results.empty:
                best_match = df_results.iloc[0]
                if best_match['distance'] < 0.4:  # Adjust threshold as needed
                    return os.path.basename(os.path.dirname(best_match['identity']))
        return "unknown"
    except Exception as e:
        logging.error(f"Error in matching face: {e}")
        return "unknown"

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
    global unknown_detected_time, recording, non_detected_counter, out, current_recording_name

    faces = detect_faces_yolo(frame)  # Use YOLOv8 for face detection
    recognized_faces = []
    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        person_name = match_face(face)
        recognized_faces.append((person_name, (x, y, w, h)))

    # Check if unknown faces are present
    unknown_faces_present = any(person_name == 'unknown' for person_name, _ in recognized_faces)

    # Logic to start and stop recording
    if unknown_faces_present:
        non_detected_counter = 0
        if not unknown_detected_time:
            unknown_detected_time = datetime.datetime.now()
        else:
            elapsed_time = (datetime.datetime.now() - unknown_detected_time).total_seconds()
            if elapsed_time >= 2 and not recording:
                # Start recording
                now = datetime.datetime.now()
                formatted_now = now.strftime("%d-%m-%y-%H-%M-%S")
                current_recording_name = os.path.join(RECORDINGS_DIR, f'{formatted_now}.mp4')
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
                out = cv2.VideoWriter(current_recording_name, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                recording = True
                print(f"Recording started at {formatted_now}")
    else:
        unknown_detected_time = None
        non_detected_counter += 1
        if non_detected_counter >= 50 and recording:
            # Stop recording and release the writer
            if out:
                out.release()
                out = None
                recording = False
                print(f"Recording stopped. Video saved: {current_recording_name}")

                # Call handle_detection to upload video to Google Cloud Storage
                from storage import handle_detection
                handle_detection(current_recording_name)
            non_detected_counter = 0

    # Write frame to the video if recording
    if recording and out:
        out.write(frame)

    # Call alert checker in a separate thread and pass the faces detected
    start_alert_thread(faces)  # Start alert check thread

    return recognized_faces
