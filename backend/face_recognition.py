import os
import cv2
import datetime
from PIL import Image
import pandas as pd
from alert import start_alert_thread
from storage import handle_detection
import tensorflow as tf
import cupy as cp
from retinaface import RetinaFace  # Import RetinaFace for face detection

# Set the GPU allocator to enable asynchronous memory allocation
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("TensorFlow GPU ready.")
    except RuntimeError as e:
        print(f"TensorFlow error: {e}")

# Test CuPy
try:
    gpu_array = cp.zeros((100, 100))
    print("CuPy GPU ready.")
except Exception as e:
    print(f"CuPy error: {e}")

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


def face_database(dataset_path):
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
    return pd.DataFrame(face_db)


def recognize_faces(frame):
    global unknown_detected_time, recording, non_detected_counter, out, current_recording_name

    faces = detect_faces_retinaface(frame, min_face_size=(150, 150))
    recognized_faces = []

    for (x, y, w, h) in faces:
        face = frame[y:y + h, x:x + w]
        person_name, confidence = match_face(face, dataset_path)
        
        # Skip ignored faces
        if person_name != "ignore":
            recognized_faces.append((person_name, confidence, (x, y, w, h)))

    unknown_faces_present = any(person_name == 'unknown' for person_name, _, _ in recognized_faces)

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
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(current_recording_name, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                recording = True
                print(f"Recording started at {formatted_now}")
    else:
        unknown_detected_time = None
        non_detected_counter += 1
        if non_detected_counter >= 50 and recording:
            if out:
                out.release()
                out = None
                recording = False
                print(f"Recording stopped. Video saved: {current_recording_name}")
                handle_detection(current_recording_name)
            non_detected_counter = 0

    if recording and out:
        out.write(frame)

    # Trigger alert logic
    start_alert_thread(recognized_faces)

    # Debug output to verify structure
    print("Recognized Faces:", recognized_faces)

    return recognized_faces


import cv2 
from deepface import DeepFace
import torch  # Import torch for checking CUDA
import pandas as pd  # For handling the DataFrame

# Choose the model for face recognition: 'ArcFace' or 'Facenet512'
face_recognition_model = "Facenet512"  # Change to "ArcFace" for ArcFace

def smooth_frame(frame):
    # Apply Gaussian Blur to smoothen the frame
    return cv2.GaussianBlur(frame, (5, 5), 0)

def match_face(face, dataset_path):
    try:
        # Use the selected face recognition model (either ArcFace or Facenet512)
        results = DeepFace.find(face, db_path=dataset_path, model_name=face_recognition_model, distance_metric="cosine", enforce_detection=False)
        
        if isinstance(results, list) and len(results) > 0:
            df_results = results[0]  # The first element contains a DataFrame
            if isinstance(df_results, pd.DataFrame) and not df_results.empty:
                best_match = df_results.iloc[0]
                distance = best_match['distance']
                threshold = 1  # Distance threshold for recognition
                
                if distance < threshold:
                    confidence = round((1 - distance / threshold) * 100, 2)  # Confidence as a percentage
                    
                    # Ignore confidence scores between 1% and 69%
                    if confidence >= 90:
                        name = os.path.basename(os.path.dirname(best_match['identity']))
                        return name, confidence
                    elif confidence > 0 and confidence < 90:
                        # Ignore mid-range scores
                        return "ignore", 0.0
        
        # Default to unknown if no match is found
        return "unknown", 0.0
    
    except Exception as e:
        print(f"Face matching error: {e}")
        return "unknown", 0.0


def detect_faces_retinaface(frame, min_face_size=(150, 150), threshold=0.7):
    """
    Detect faces using RetinaFace with a minimum face size to shorten the detection range.
    
    :param frame: The image frame in which faces are to be detected.
    :param min_face_size: The minimum size of the face to be detected, default is (100, 100) for closer faces.
    :param threshold: The confidence threshold for face detection, default is 0.7.
    :return: List of detected faces in (x, y, w, h) format.
    """
    # Perform face detection with RetinaFace
    faces = RetinaFace.detect_faces(frame)
    detected_faces = []

    for key in faces:
        # Extract the facial area
        facial_area = faces[key]["facial_area"]
        x, y, w, h = facial_area

        # Only include faces larger than the minimum size to focus on nearby faces
        if w >= min_face_size[0] and h >= min_face_size[1]:
            detected_faces.append((x, y, w - x, h - y))  # Convert to (x, y, w, h) format
    
    return detected_faces