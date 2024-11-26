import cv2
from vidgear.gears import CamGear
from face_recognition import recognize_faces
from alert import check_alert
import logging
from utils.camera_utils import camera_streams
from concurrent.futures import ThreadPoolExecutor
import cupy as cp

# Initialize a thread pool executor with a max number of workers (4 in this example)
executor = ThreadPoolExecutor(max_workers=4)

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
                    recognized_faces = recognize_faces(frame)

                    check_alert(recognized_faces)

                    for person_name, confidence, (x, y, w, h) in recognized_faces:
                        label = f"{person_name} ({confidence:.2f}%)"
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        
                    #cv2.imshow(f"Camera {camera_id}", frame)

                    #if cv2.waitKey(1) & 0xFF == ord('q'):
                    #    break

                    
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    frame_bytes = buffer.tobytes()

                    socketio.emit('video_frame', {'camera_id': camera_id, 'frame': frame_bytes})
                else:
                    break

            stream.stop()
            print(f"Camera {camera_id} released.")

        # Submit the stream task to the thread pool
        executor.submit(stream)




def start_camera(camera_ip, camera_streams, recognize_faces, check_alert, socketio):
    
    
    # Use CamGear for webcam or RTSP streams
    stream = CamGear(source=int(camera_ip)).start()  # For webcam, pass the index; for RTSP, pass the URL
    
    if not stream:
        print(f"Failed to open camera {camera_ip}")
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



            #cv2.imshow(f"Camera {camera_ip}", frame)

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
            
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            frame_bytes = buffer.tobytes()
            socketio.emit('video_frame', {'camera_ip': camera_ip, 'frame': frame_bytes})
            
        else:
            break

    stream.stop()
    cv2.destroyAllWindows()
