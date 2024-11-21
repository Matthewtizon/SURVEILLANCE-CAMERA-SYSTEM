import pygame
import time
import threading
from notifications import send_notification  # Import send_notification here

# Initialize Pygame for sound
pygame.mixer.init()

# Load alert sound
alert_sound = pygame.mixer.Sound("alert.mp3")  # Ensure you have an alert.mp3 file in the same directory

# Variables to keep track of unknown face detection
unknown_face_detected = False
last_detection_time = 0
detection_threshold = 2  # Time in seconds for how long the face should be on screen to trigger the alert
alert_triggered = False  # Flag to track if the alert has already been triggered

# Function to play the alert sound
def play_alert():
    pygame.mixer.Sound.play(alert_sound)

# Function to check for unknown faces and trigger the alert if necessary
def check_alert(faces):
    global unknown_face_detected, last_detection_time, alert_triggered

    current_time = time.time()

    # Check if any face in the list has been labeled 'unknown'
    for face in faces:
        person_name, _ = face  # Unpack the name and bounding box
        if person_name.lower() == 'unknown':
            if not unknown_face_detected:
                unknown_face_detected = True
                last_detection_time = current_time  # Start the timer when an unknown face is detected

            # If the unknown face has been detected for more than the threshold and alert not yet triggered
            if current_time - last_detection_time >= detection_threshold and not alert_triggered:
                play_alert()  # Play the alert sound
                # send_notification("URL of the camera or relevant information")  # Uncomment to send a notification
                alert_triggered = True  # Mark the alert as triggered
            break  # Exit the loop once an unknown face is detected
    else:
        # Reset the detection status if no unknown faces are present
        unknown_face_detected = False
        last_detection_time = 0
        alert_triggered = False  # Reset the alert so it can be triggered again in the future




# Function to run the alert checker in a separate thread
def start_alert_thread(faces):
    # Start a separate thread to check for unknown faces
    threading.Thread(target=check_alert, args=(faces,), daemon=True).start()  # Pass 'faces' to check_alert
