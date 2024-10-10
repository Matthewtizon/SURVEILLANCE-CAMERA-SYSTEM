import cv2
import os
import numpy as np
from deepface import DeepFace
import tensorflow as tf

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

# Initialize video capture
cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if necessary
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Path to dataset
dataset_path = 'dataset'

# Load dataset images
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

# Load dataset
dataset = load_dataset(dataset_path)

# Match face with dataset
def match_face(face):
    global dataset

    for person_name, images in dataset.items():
        for ref_img in images:
            try:
                # Match face with a reference image from the dataset
                result = DeepFace.verify(
                    face,
                    ref_img,
                    model_name='VGG-Face',
                    enforce_detection=False,
                    detector_backend='skip'  # Skip internal detection since faces are already cropped
                )
                if result['verified']:
                    return person_name
            except ValueError:
                continue
            except Exception as e:
                print(f"Error during face verification: {e}")
                continue
    return 'unknown'

# Detect faces using SSD
def detect_faces_ssd(frame):
    (h, w) = frame.shape[:2]
    # Prepare input blob for the SSD model
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
        if confidence > 0.5:  # Minimum confidence to filter weak detections
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            # Ensure the bounding box coordinates are within the frame dimensions
            x, y = max(0, x), max(0, y)
            x1, y1 = min(w, x1), min(h, y1)
            faces.append((x, y, x1 - x, y1 - y))
    return faces

while True:
    ret, frame = cap.read()
    if ret:
        # Detect faces using SSD
        faces = detect_faces_ssd(frame)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]

            # Match the face in the dataset
            person_name = match_face(face)

            # Draw a rectangle around the face and label it
            color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(
                frame,
                f"{person_name.upper()}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

        # Display the frame with face recognition results
        cv2.imshow("video", frame)

        # Break the loop if 'q' is pressed
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
