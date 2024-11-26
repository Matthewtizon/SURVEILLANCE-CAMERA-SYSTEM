import cv2 
from deepface import DeepFace
from ultralytics import YOLO  # For YOLOv8
import torch  # Import torch for checking CUDA
import os
import pandas as pd  # For handling the DataFrame

# Load YOLOv8 model for face detection with GPU support
device = "cuda" if torch.cuda.is_available() else "cpu"
yolo_model = YOLO("yolov8n_100e.pt").to(device)  # Pre-trained YOLOv8-Tiny for face detection

# Choose the model for face recognition: 'ArcFace' or 'Facenet512'
face_recognition_model = "VGG-Face"  # Change to "ArcFace" for ArcFace

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
                threshold = 0.4  # Distance threshold for recognition
                if distance < threshold:
                    confidence = round((1 - distance / threshold) * 100, 2)  # Confidence as a percentage
                    name = os.path.basename(os.path.dirname(best_match['identity']))
                    return name, confidence
        return "unknown", 0.0
    except Exception as e:
        print(f"Face matching error: {e}")
        return "unknown", 0.0



def detect_faces_yolo(frame):
    # Perform face detection with YOLO on the selected device
    results = yolo_model.predict(frame, conf=0.5)  # Confidence threshold at 50%
    detections = results[0].boxes  # Get bounding boxes

    faces = []
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])  # Extract bounding box coordinates
        faces.append((x1, y1, x2 - x1, y2 - y1))  # Convert to (x, y, w, h) format
    return faces
