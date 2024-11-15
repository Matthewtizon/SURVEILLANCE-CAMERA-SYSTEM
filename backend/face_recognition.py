import cv2
import os
import numpy as np
from deepface import DeepFace
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity

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
ssd_prototxt = "deploy.prototxt"
face_net = cv2.dnn.readNetFromCaffe(ssd_prototxt, ssd_model)

# Path to dataset
dataset_path = 'dataset'

def load_dataset_with_embeddings(dataset_path):
    dataset_embeddings = {}
    for person_folder in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_folder)
        if os.path.isdir(person_path):
            embeddings = []
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path)
                if img is not None:
                    try:
                        # Resize image before generating embedding
                        img = cv2.resize(img, (224, 224))  # Resize to VGG-Face expected input size
                        embedding = DeepFace.represent(img, model_name='VGG-Face', enforce_detection=False)
                        print(f"Generated embedding for {img_name}: {embedding}")
                        embeddings.append(embedding[0]['embedding'])
                    except Exception as e:
                        print(f"Error generating embedding for {img_name}: {e}")
            dataset_embeddings[person_folder] = embeddings
    return dataset_embeddings



# Use precomputed embeddings for face matching
dataset_embeddings = load_dataset_with_embeddings(dataset_path)

# Match face with dataset
def match_face(face):
    global dataset_embeddings

    # Generate embedding for the detected face
    try:
        face_embedding = DeepFace.represent(face, model_name='VGG-Face', enforce_detection=False)[0]['embedding']
    except Exception as e:
        print(f"Error generating embedding for the face: {e}")
        return 'unknown'

    best_match = ('unknown', 0)  # Default to 'unknown' with the lowest similarity score

    # Compare embedding with dataset embeddings
    for person_name, embeddings in dataset_embeddings.items():
        for ref_embedding in embeddings:
            # Calculate cosine similarity
            similarity = cosine_similarity([face_embedding], [ref_embedding])[0][0]
            if similarity > best_match[1]:  # Track highest similarity score
                best_match = (person_name, similarity)

    # Define a threshold for recognizing a person
    threshold = 0.4  # Adjust this as necessary
    return best_match[0] if best_match[1] >= threshold else 'unknown'

# Detect faces using SSD
def detect_faces_ssd(frame):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )
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

# Process each frame for face recognition
def recognize_faces(frame):
    faces = detect_faces_ssd(frame)
    results = []
    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        person_name = match_face(face)
        results.append((person_name, (x, y, w, h)))
    return results
