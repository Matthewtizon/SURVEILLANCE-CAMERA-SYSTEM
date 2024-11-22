import cv2
from deepface import DeepFace
from ultralytics import YOLO  # For YOLOv8
import os
import pandas as pd  # For handling the DataFrame

# Load YOLOv8 model for face detection
yolo_model = YOLO("yolov8n_100e.pt")  # Pre-trained YOLOv8-Tiny for face detection


def match_face(face, dataset_path):
    try:
        results = DeepFace.find(face, db_path=dataset_path, model_name="VGG-Face", distance_metric="cosine", enforce_detection=False)
        if isinstance(results, list) and len(results) > 0:
            df_results = results[0]  # The first element contains a DataFrame
            if isinstance(df_results, pd.DataFrame) and not df_results.empty:
                best_match = df_results.iloc[0]
                if best_match['distance'] < 0.4:
                    return os.path.basename(os.path.dirname(best_match['identity']))
        return "unknown"
    except Exception as e:
        print(f"Face matching error: {e}")
        return "unknown"


def detect_faces_yolo(frame):
    results = yolo_model.predict(frame, conf=0.5)  # Confidence threshold at 50%
    detections = results[0].boxes  # Get bounding boxes

    faces = []
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])  # Extract bounding box coordinates
        faces.append((x1, y1, x2 - x1, y2 - y1))  # Convert to (x, y, w, h) format
    return faces
