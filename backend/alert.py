import pygame
import time
import threading

# Initialize Pygame for sound
pygame.mixer.init()

# Load alert sound
alert_sound = pygame.mixer.Sound("alert.mp3")  # Ensure alert.mp3 exists in the same directory

# Variables to track unknown face detection
last_detection_time = None
alert_triggered = False
detection_threshold = 2  # Time in seconds to trigger the alert

# Function to play the alert sound
def play_alert():
    pygame.mixer.Sound.play(alert_sound)

# Function to check for unknown faces and trigger alert if necessary
def check_alert(faces):
    global last_detection_time, alert_triggered

    current_time = time.time()

    # Check if an unknown face is detected
    unknown_face_detected = any(
        isinstance(face, tuple) and len(face) >= 1 and face[0].lower() == 'unknown' for face in faces
    )

    if unknown_face_detected:
        # Start the detection timer if it's the first detection
        if not last_detection_time:
            last_detection_time = current_time
        else:
            # Check if detection has lasted beyond the threshold
            elapsed_time = current_time - last_detection_time
            if elapsed_time >= detection_threshold and not alert_triggered:
                play_alert()
                print("ALERT: Unknown face detected!")
                alert_triggered = True
    else:
        # Reset tracking variables if no unknown face is detected
        last_detection_time = None
        alert_triggered = False

# Function to run the alert checker in a separate thread
def start_alert_thread(faces):
    threading.Thread(target=check_alert, args=(faces,), daemon=True).start()
