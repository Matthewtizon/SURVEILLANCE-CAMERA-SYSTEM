import cv2
import os
import numpy as np
from ultralytics import YOLO

def is_blurry(image, threshold=100):
    """
    Detects blur in the image using the Laplacian method.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def apply_blur(face_image, kernel_size=(7, 7)):
    """
    Applies Gaussian blur to an image.

    Args:
        face_image (np.ndarray): Image to blur.
        kernel_size (tuple): Kernel size for Gaussian blur.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.GaussianBlur(face_image, kernel_size, 0)


def augment_data(face_image, num_augmented_images=3):
    """
    Applies data augmentation to a face image using OpenCV.

    Args:
        face_image (np.ndarray): Cropped face image.
        num_augmented_images (int): Number of augmented images to generate.

    Returns:
        list: List of augmented images.
    """
    augmented_images = []
    h, w, _ = face_image.shape

    for i in range(num_augmented_images):
        # Random Horizontal Flip
        if np.random.rand() > 0.5:
            flipped = cv2.flip(face_image, 1)
            augmented_images.append(flipped)
        
        # Random Rotation
        angle = np.random.uniform(-15, 15)
        rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1)
        rotated = cv2.warpAffine(face_image, rotation_matrix, (w, h))
        augmented_images.append(rotated)

        # Random Brightness Adjustment
        brightness_factor = np.random.uniform(0.8, 1.2)
        brightness_adjusted = cv2.convertScaleAbs(face_image, alpha=brightness_factor, beta=0)
        augmented_images.append(brightness_adjusted)
    
    return augmented_images

def apply_resize(face_image, target_size=(256, 256)):
    """
    Resizes an image to the target size.

    Args:
        face_image (np.ndarray): Image to resize.
        target_size (tuple): Target size (width, height).

    Returns:
        np.ndarray: Resized image.
    """
    return cv2.resize(face_image, target_size)



def create_face_dataset(person_name, num_images=500, output_dir='backend/dataset', model_path='backend/yolov8n_100e.pt'):
    person_dir = os.path.join(output_dir, person_name)

    if os.path.exists(person_dir):
        print(f"Dataset for '{person_name}' already exists at {person_dir}. Aborting.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.makedirs(person_dir)

    model = YOLO(model_path)
    cap = cv2.VideoCapture(0)

    print(f"Capturing {num_images} images for {person_name}. Press 'q' to quit early.")
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access the webcam.")
            break

        results = model(frame, conf=0.5)
        detections = results[0].boxes.data.cpu().numpy()

        if detections.size > 0:
            largest_box = max(detections, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))
            x1, y1, x2, y2, conf, cls = map(int, largest_box[:6])

            if cls == 0:
                face_crop = frame[y1:y2, x1:x2]

                if is_blurry(face_crop):
                    print("Skipped a blurry image.")
                    continue

                # Data augmentation
                augmented_faces = augment_data(face_crop, num_augmented_images=3)

                for img in augmented_faces:
                    # Apply additional processing if needed
                    blurred = apply_blur(img)
                    resized = apply_resize(blurred, target_size=(256, 256))

                    file_path = os.path.join(person_dir, f"{person_name}_{count}.jpg")
                    cv2.imwrite(file_path, resized)
                    count += 1
                    if count >= num_images:
                        break

                # Draw green bounding box for visualization
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Closest Face", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow(f"Capturing Faces for {person_name}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting early.")
            break

    print(f"Captured {count} images for {person_name}.")
    cap.release()
    cv2.destroyAllWindows()


# Example usage
#create_face_dataset(person_name="Matthew", num_images=500, model_path='backend/yolov8n_100e.pt')
