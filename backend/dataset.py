import cv2
import os
import numpy as np
from ultralytics import YOLO
import dlib  # For face alignment

def is_blurry(image, threshold=100):
    """
    Detects blur in the image using the Laplacian method.

    Args:
        image (np.ndarray): Input image.
        threshold (int): Threshold for blur detection. Lower values indicate more blur.

    Returns:
        bool: True if the image is blurry, False otherwise.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def augment_image(image):
    """
    Applies real-time data augmentation to the image.

    Args:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Augmented image.
    """
    # Flip the image horizontally
    flipped = cv2.flip(image, 1)
    # Adjust brightness
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = cv2.add(hsv[:, :, 2], np.random.randint(-30, 30))  # Random brightness adjustment
    adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return [image, flipped, adjusted]

def align_face(image, rect):
    """
    Aligns a face in the image based on landmarks.

    Args:
        image (np.ndarray): Input image.
        rect (dlib.rectangle): Bounding box of the detected face.

    Returns:
        np.ndarray: Aligned face crop.
    """
    predictor_path = 'backend/shape_predictor_68_face_landmarks.dat'  # Ensure this file is downloaded
    predictor = dlib.shape_predictor(predictor_path)
    shape = predictor(image, rect)
    # Convert landmarks to numpy array
    landmarks = np.array([(p.x, p.y) for p in shape.parts()])
    # Calculate the center between the eyes
    left_eye = landmarks[36:42].mean(axis=0)
    right_eye = landmarks[42:48].mean(axis=0)
    # Rotate and crop the face based on eye alignment
    angle = np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]) * 180 / np.pi
    M = cv2.getRotationMatrix2D(tuple(left_eye), angle, 1)
    aligned = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    return aligned

def create_face_dataset(person_name, num_images=200, output_dir='backend/dataset', model_path='backend/yolov8n_100e.pt'):
    """
    Captures face images from a webcam using YOLOv8 for face detection and saves them in a specified directory.

    Args:
        person_name (str): The name of the person (directory will be created under `output_dir`).
        num_images (int): The number of face images to capture.
        output_dir (str): The root directory where datasets are stored.
        model_path (str): Path to the YOLOv8 model file.
    """
    # Path to the person's directory
    person_dir = os.path.join(output_dir, person_name)
    
    # Check if the person's directory already exists
    if os.path.exists(person_dir):
        print(f"Dataset for '{person_name}' already exists at {person_dir}. Aborting.")
        return

    # Create the dataset directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a subdirectory for the person
    os.makedirs(person_dir)

    # Load the YOLOv8 model
    model = YOLO(model_path)
    
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    print(f"Capturing {num_images} images for {person_name}. Press 'q' to quit early.")
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access the webcam.")
            break

        # Perform face detection using YOLOv8
        results = model(frame, conf=0.5)
        detections = results[0].boxes.data.cpu().numpy()  # Extract detection results

        for detection in detections:
            x1, y1, x2, y2, conf, cls = map(int, detection[:6])  # Extract bounding box coordinates and class
            if cls == 0:  # Assuming '0' is the class ID for 'face'
                face_crop = frame[y1:y2, x1:x2]

                # Quality Control: Check for blurriness
                if is_blurry(face_crop):
                    print("Skipped a blurry image.")
                    continue

                # Face Alignment
                rect = dlib.rectangle(x1, y1, x2, y2)
                aligned_face = align_face(frame, rect)

                # Data Augmentation
                augmented_faces = augment_image(aligned_face)

                # Save augmented images
                for img in augmented_faces:
                    file_path = os.path.join(person_dir, f"{person_name}_{count}.jpg")
                    cv2.imwrite(file_path, img)
                    count += 1
                    if count >= num_images:
                        break

                # Stop if the required number of images is reached
                if count >= num_images:
                    print(f"Captured {num_images} images for {person_name}.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return

        # Display the frame with detected faces
        cv2.imshow(f"Capturing Faces for {person_name}", frame)

        # Quit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting early.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Example usage
create_face_dataset(person_name="Matthew", num_images=200, model_path='backend/yolov8n_100e.pt')
