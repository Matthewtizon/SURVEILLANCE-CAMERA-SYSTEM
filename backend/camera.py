import cv2
from vidgear.gears import CamGear
from face_recognition import recognize_faces
from alert import check_alert
import logging
from utils.camera_utils import camera_streams
from concurrent.futures import ThreadPoolExecutor
import signal
import time

# Replace existing camera_streams with camera_streams_dict
camera_streams_dict = {}
camera_streams = camera_streams

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# JPEG quality as a configurable parameter
JPEG_QUALITY = 50

# ThreadPoolExecutor for parallel camera processing
executor = ThreadPoolExecutor(max_workers=5)  # Adjust based on resources

# Graceful shutdown handler
def shutdown_handler(signum, frame):
    logging.info("Shutting down all camera streams.")
    for stream in camera_streams_dict.values():
        if stream:
            stream.stop()

# Register shutdown signals
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def process_frame(camera_id, frame, socketio):
    """Processes a frame: face recognition, alerts, encoding, and emitting."""
    try:
        recognized_faces = recognize_faces(frame)

        for person_name, confidence, (x, y, w, h) in recognized_faces:
            label = f"{person_name} ({confidence:.2f}%)"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        check_alert(recognized_faces)  # Trigger alerts based on detection

        # Encode the frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        frame_bytes = buffer.tobytes()

        # Emit the frame over socket
        socketio.emit('video_frame', {'camera_id': camera_id, 'frame': frame_bytes})
    except Exception as e:
        logging.error(f"Error processing frame for camera {camera_id}: {e}")

def start_ip_camera(app, camera_id, Camera, socketio):
    """Start a camera stream."""
    with app.app_context():
        camera = Camera.query.get(camera_id)
        if not camera:
            logging.error(f"Camera with ID {camera_id} not found.")
            return

        rtsp_url = camera.rtsp_url
        logging.info(f"Starting stream for camera ID {camera_id} at {rtsp_url}.")

        stream = CamGear(
            source=rtsp_url,
            logging=True,
            backend="FFMPEG",
            **{"THREADED_QUEUE_MODE": False, "time_delay": 0}
        ).start()

        if stream.read() is None:
            logging.error(f"Failed to open camera {camera_id} with RTSP URL: {rtsp_url}")
            return

        camera_streams_dict[camera_id] = stream

        try:
            while camera_id in camera_streams_dict:
                frame = stream.read()
                if frame is None:
                    logging.warning(f"Stream lost for camera {camera_id}. Attempting reconnection.")
                    stream.stop()
                    time.sleep(5)  # Retry after delay
                    stream = CamGear(source=rtsp_url).start()
                    continue

                process_frame(camera_id, frame, socketio)
                time.sleep(0.033)  # ~30 FPS

                #cv2.imshow(f"Camera {camera_id}", frame)

                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
        except Exception as e:
            logging.error(f"Error during stream processing for camera {camera_id}: {e}")
        finally:
            stream.stop()
            del camera_streams_dict[camera_id]
            logging.info(f"Camera {camera_id} stream stopped.")

def start_web_camera(camera_ip, camera_streams, recognize_faces, check_alert, socketio):
    # Use CamGear for webcam or RTSP streams
    stream = CamGear(source=int(camera_ip)).start()  # For webcam, pass the index; for RTSP, pass the URL
    
    if not stream:
        logging.error(f"Failed to open camera {camera_ip}")
        return

    while camera_ip in camera_streams:
        frame = stream.read()
        if frame is not None:
            recognized_faces = recognize_faces(frame)            

            check_alert(recognized_faces)

            for person_name, confidence, (x, y, w, h) in recognized_faces:
                label = f"{person_name} ({confidence:.2f}%)"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.imshow(f"Camera {camera_ip}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Send frame to frontend via socket
            #_, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            #frame_bytes = buffer.tobytes()
            #socketio.emit('video_frame', {'camera_ip': camera_ip, 'frame': frame_bytes})
            
        else:
            logging.warning(f"Stream from camera {camera_ip} returned None, stopping.")
            break

    stream.stop()
    cv2.destroyAllWindows()