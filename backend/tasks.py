from celery_config import app
import cv2
import os
import numpy as np
import gc
import redis
import base64
from deepface import DeepFace
from io import BytesIO

# Set up Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Load SSD face detector
ssd_model = "res10_300x300_ssd_iter_140000.caffemodel"
ssd_prototxt = "deploy.prototxt"
face_net = cv2.dnn.readNetFromCaffe(ssd_prototxt, ssd_model)

# Load the dataset for facial recognition
def load_dataset(dataset_path):
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

# Define the Celery task to process an encoded video frame
@app.task(bind=True)
def process_frame(self, frame_encoded, dataset_path="backend/dataset"):
    """Process an encoded frame for face detection and recognition."""
    
    # Decode the base64-encoded frame back into an image
    frame_data = base64.b64decode(frame_encoded)
    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Load the dataset for matching
    dataset = load_dataset(dataset_path)

    # Detect faces using SSD
    faces = detect_faces_ssd(frame)

    results = []  # Store recognition results

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]

        # Match the face with the dataset
        person_name = match_face(face, dataset)

        # Draw a rectangle around the face
        color = (0, 255, 0) if person_name != 'Unknown' else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        results.append({
            "name": person_name,
            "box": (x, y, w, h)
        })

    # Save the processed frame as an image file
    output_image_path = f"processed_frames/{self.request.id}.jpg"
    cv2.imwrite(output_image_path, frame)

    # Store results in Redis as a JSON string
    redis_client.set(self.request.id, str(results))

    return {
        "image_path": output_image_path,  # Return image path
        "results": results  # Return recognition results
    }

def detect_faces_ssd(frame):
    """Detect faces in a frame using SSD."""
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

def match_face(face, dataset):
    """Match detected face with faces in the dataset."""
    for person_name, images in dataset.items():
        for ref_img in images:
            try:
                # Using 'Facenet' model for matching
                result = DeepFace.verify(face, ref_img, model_name='Facenet', enforce_detection=False, detector_backend='skip')
                if result['verified']:
                    return person_name
            except Exception as e:
                print(f"Error during face verification: {e}")
                continue
    return 'Unknown'
