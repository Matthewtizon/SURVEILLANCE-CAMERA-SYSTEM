import cv2
import os
import numpy as np
from retinaface import RetinaFace  # Import RetinaFace for face detection

def is_blurry(image, threshold=100):
    """
    Detects blur in the image using the Laplacian method.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def augment_image(image):
    """
    Applies real-time data augmentation to the image.
    """
    augmented_images = []

    # Original image
    augmented_images.append(image)

    # Flip horizontally
    flipped = cv2.flip(image, 1)
    augmented_images.append(flipped)

    # Brightness adjustment
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brightness_factor = np.random.randint(-30, 30)
    hsv[:, :, 2] = cv2.add(hsv[:, :, 2], brightness_factor)
    brightness_adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    augmented_images.append(brightness_adjusted)

    return augmented_images

def create_face_dataset(person_name, num_images=200, output_dir='backend/dataset'):
    """
    Captures face images from a webcam using RetinaFace for face detection and saves them in a specified directory.
    """
    person_dir = os.path.join(output_dir, person_name)

    if os.path.exists(person_dir):
        print(f"Dataset for '{person_name}' already exists at {person_dir}. Aborting.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.makedirs(person_dir)

    cap = cv2.VideoCapture(0)

    print(f"Capturing {num_images} images for {person_name}. Press 'q' to quit early.")
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access the webcam.")
            break

        # Perform face detection with RetinaFace
        detections = RetinaFace.detect_faces(frame)

        if detections:
            # Find the closest face based on the size of the bounding box
            largest_face = max(
                detections.values(),
                key=lambda face: (face["facial_area"][2] - face["facial_area"][0]) *
                                 (face["facial_area"][3] - face["facial_area"][1])
            )
            x1, y1, x2, y2 = largest_face["facial_area"]

            face_crop = frame[y1:y2, x1:x2]

            if is_blurry(face_crop):
                print("Skipped a blurry image.")
                continue

            augmented_faces = augment_image(face_crop)

            for img in augmented_faces:
                file_path = os.path.join(person_dir, f"{person_name}_{count}.jpg")
                cv2.imwrite(file_path, img)
                count += 1
                if count >= num_images:
                    break

            # Draw a green bounding box around the closest face
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Closest Face", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show the frame and move the window to the center
        cv2.imshow(f"Capturing Faces for {person_name}", frame)
        
        # Get screen size and center the window
        screen_width = 1920  # Replace with your screen width
        screen_height = 1080  # Replace with your screen height
        window_width = 640  # Replace with the desired window width
        window_height = 480  # Replace with the desired window height

        # Calculate the position for the window to be centered
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2

        # Move the window to the calculated position
        cv2.moveWindow(f"Capturing Faces for {person_name}", x_pos, y_pos)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting early.")
            break

    print(f"Captured {count} images for {person_name}.")
    cap.release()
    cv2.destroyAllWindows()
