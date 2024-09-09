import cv2
from simple_facerec import SimpleFacerec
import time
import os
import logging
import ffmpeg
from playsound import playsound  # Import playsound library

class Camera:
    def __init__(self, encoding_images_path):
         # Enable OpenCV optimizations
        cv2.setUseOptimized(True)
        cv2.setNumThreads(4)  # Adjust based on your CPU's cores

        # Initialize the face recognition system
        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_images(encoding_images_path)
        
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        
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

    def get_frame(self):
        """
        Capture a frame from the camera, perform face recognition, 
        and return the processed frame.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to grab frame")

        # Detect faces
        face_locations, face_names = self.sfr.detect_known_faces(frame)

        if not face_names:
            # No faces detected
            self.no_face_frames += 1
            if self.no_face_frames >= self.max_no_face_frames and self.recording:
                self.stop_recording()
        else:
            self.no_face_frames = 0
            if "Unknown" in face_names and not self.recording:
                self.start_recording()
                self.play_alert_sound()  # Play alert sound when an unknown face is detected

        # Draw rectangles and names around detected faces
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

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
camera_instance = Camera("images/")

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
