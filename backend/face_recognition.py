import os
import cv2
import datetime
from PIL import Image
import pandas as pd
from recognize_faces import match_face, detect_faces_yolo
from alert import start_alert_thread
from storage import handle_detection
import tensorflow as tf
import cupy as cp


gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
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

    faces = detect_faces_yolo(frame)
    recognized_faces = []
    for (x, y, w, h) in faces:
        face = frame[y:y + h, x:x + w]
        person_name, confidence = match_face(face, dataset_path)  # Pass the dataset_path here
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
