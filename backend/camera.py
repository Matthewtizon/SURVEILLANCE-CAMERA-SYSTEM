import cv2
from simple_facerec import SimpleFacerec

class Camera:
    def __init__(self, encoding_images_path):
        # Initialize the face recognition system
        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_images(encoding_images_path)
        
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

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

        # Draw rectangles and names around detected faces
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        return frame

    def release(self):
        """Release the camera and close any open windows."""
        self.cap.release()

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
            print(f"Camera monitoring error: {e}")
            break
    camera_instance.release()
