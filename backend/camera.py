import cv2
import time
import os
import logging
import ffmpeg
from playsound import playsound  # Import playsound library
from deepface import DeepFace
import numpy as np
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

class Camera:
    def __init__(self, dataset_path):
        # Set OpenCV to use all available CPU cores for better performance
        cv2.setNumThreads(cv2.getNumberOfCPUs())

        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        # Load the dataset for facial recognition
        self.dataset = self.load_dataset(dataset_path)

        # Video recording attributes
        self.recording = False
        self.video_file_path = None
        self.video_writer = None
        self.no_face_frames = 0
        self.max_no_face_frames = 30  # Adjust this value based on your requirement (e.g., 30 frames)

        # Ensure recordings directory exists
        if not os.path.exists('recordings'):
            os.makedirs('recordings')

        # Path to the alert sound file
        self.alert_sound_path = os.path.join(os.path.dirname(__file__), 'alert.wav')

    def load_dataset(self, dataset_path):
        """
        Load the dataset images for face matching.
        """
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

    def match_face(self, face):
        """
        Match detected face with faces in the dataset.
        """
        for person_name, images in self.dataset.items():
            for ref_img in images:
                try:
                    result = DeepFace.verify(face, ref_img, model_name='VGG-Face', enforce_detection=False, detector_backend='skip')
                    if result['verified']:
                        return person_name
                except Exception as e:
                    print(f"Error during face verification: {e}")
                    continue
        return 'Unknown'

    def start_recording(self):
        """Start recording the video."""
        self.recording = True
        self.video_file_path = f"recordings/{time.strftime('%Y%m%d-%H%M%S')}.mp4"
        self.video_writer = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s='640x480').output(
            self.video_file_path, vcodec='libx264', pix_fmt='yuv420p'
        ).overwrite_output().run_async(pipe_stdin=True)

    def stop_recording(self):
        """Stop recording the video and save the file."""
        self.recording = False
        if self.video_writer is not None:
            self.video_writer.stdin.close()
            self.video_writer.wait()
            self.video_writer = None

    def play_alert_sound(self):
        """Play the alert sound."""
        playsound(self.alert_sound_path)

    def detect_faces_ssd(self, frame):
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

    def get_frame(self):
        """
        Capture a frame from the camera, perform face detection and recognition, 
        and return the processed frame.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to grab frame")

        # Detect faces using SSD
        faces = self.detect_faces_ssd(frame)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]

            # Match the face in the dataset
            person_name = self.match_face(face)

            # Draw a rectangle around the face and label it
            color = (0, 255, 0) if person_name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{person_name.upper()}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            if person_name == "Unknown" and not self.recording:
                self.start_recording()
                self.play_alert_sound()  # Play alert sound when an unknown face is detected

        # Stop recording if no face is detected for some time
        if not faces:
            self.no_face_frames += 1
            if self.no_face_frames >= self.max_no_face_frames and self.recording:
                self.stop_recording()
        else:
            self.no_face_frames = 0

        # Write the frame to the video file if recording
        if self.recording and self.video_writer is not None:
            self.video_writer.stdin.write(frame.tobytes())

        return frame

    def release(self):
        """Release the camera and close any open windows."""
        self.cap.release()
        if self.video_writer is not None:
            self.video_writer.stdin.close()
            self.video_writer.wait()

# Create a singleton camera instance
camera_instance = Camera("backend/dataset")

def get_frame_from_camera():
    """Function to be used in the camera_routes.py file."""
    return camera_instance.get_frame()

def start_monitoring():
    """Function to start camera monitoring in a separate thread."""
    while True:
        try:
            frame = get_frame_from_camera()
            # Save or process frame as needed
        except Exception as e:
            logging.error(f"Camera monitoring error: {e}")
            break
    camera_instance.release()
