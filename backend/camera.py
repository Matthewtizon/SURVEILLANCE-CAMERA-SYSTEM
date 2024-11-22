import cv2
from flask_socketio import SocketIO
from vidgear.gears import CamGear
import threading
from face_recognition import recognize_faces
from alert import check_alert
import logging
from utils.camera_utils import camera_streams


# Replace existing camera_streams with camera_streams_dict
camera_streams_dict = {}
camera_streams =  camera_streams

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def start_camera_stream(app, camera_id, Camera, socketio):
    with app.app_context():
        # Fetch the camera from the database by ID
        camera = Camera.query.get(camera_id)
        if not camera:
            print(f"Camera with ID {camera_id} not found.")
            return

        rtsp_url = camera.rtsp_url

        def stream():
            frame_count = 0
            # Initialize CamGear for live stream
            stream = CamGear(
                source=rtsp_url,
                logging=True,
                backend="FFMPEG",
                **{"THREADED_QUEUE_MODE": False, "time_delay": 0}
            ).start()

            try:
                frame = stream.read()
                if frame is None:
                    print(f"Failed to open camera {camera_id} with RTSP URL: {rtsp_url}")
                    return
            except Exception as e:
                print(f"Error initializing stream for camera {camera_id}: {e}")
                return

            while camera_id in camera_streams_dict:
                frame = stream.read()
                if frame is not None:
                    if frame_count % 3 == 0:
                        recognized_faces = recognize_faces(frame)
                    frame_count += 1

                    check_alert(recognized_faces)

                    for person_name, (x, y, w, h) in recognized_faces:
                        color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, person_name.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    cv2.imshow(f"Camera {camera_id}", frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    frame_bytes = buffer.tobytes()
                    socketio.emit('video_frame', {'camera_id': camera_id, 'frame': frame_bytes})
                else:
                    break

            stream.stop()
            print(f"Camera {camera_id} released.")

        threading.Thread(target=stream).start()


def start_camera(camera_ip, camera_streams, recognize_faces, check_alert, socketio):
    frame_count = 0
    cap = cv2.VideoCapture(int(camera_ip))
    if not cap.isOpened():
        print(f"Failed to open camera {camera_ip}")
        return

    while camera_ip in camera_streams:
        ret, frame = cap.read()
        if ret:
            if frame_count % 3 == 0:
                recognized_faces = recognize_faces(frame)
            frame_count += 1

            check_alert(recognized_faces)

            for person_name, (x, y, w, h) in recognized_faces:
                color = (0, 255, 0) if person_name != 'unknown' else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, person_name.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            #cv2.imshow(f"Camera {camera_ip}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            frame_bytes = buffer.tobytes()
            socketio.emit('video_frame', {'camera_ip': camera_ip, 'frame': frame_bytes})
        else:
                break

    cap.release()
    cv2.destroyAllWindows()
