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

        # Display the frame in a window
        cv2.imshow('Video Feed', frame)

        # Add a delay to allow window updates
        cv2.waitKey(1)

        return frame

    def release(self):
        """Release the camera and close any open windows."""
        self.cap.release()
        cv2.destroyAllWindows()

def get_frame_from_camera():
    """Function to be used in the camera_routes.py file."""
    camera = Camera("images/")
    try:
        frame = camera.get_frame()
        ret, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    finally:
        camera.release()

def start_monitoring():
    """Function to start camera monitoring in a separate thread."""
    camera = Camera("images/")
    while True:
        try:
            frame = camera.get_frame()
            # Save or process frame as needed
        except Exception as e:
            print(f"Camera monitoring error: {e}")
            break
    camera.release()
