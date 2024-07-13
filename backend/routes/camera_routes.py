from flask import Blueprint, jsonify, Response
from models import Camera
from camera import frame_data
import cv2

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/stream_video/<int:id>', methods=['GET'])
def stream_video(id):
    camera = Camera.query.get_or_404(id)
    camera_location = camera.location
    
    # Simulated frame data, replace with actual frame retrieval logic
    # frame_data = get_frame_data(camera_location)
    if camera_location in frame_data:
        def generate():
            while True:
                frame = frame_data.get(camera_location)
                if frame is not None:
                    # Encode frame to JPEG bytes and then yield as response content
                    frame_encoded = cv2.imencode('.jpg', frame)[1].tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')
        
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({'error': f'No frame available for camera {id} at {camera_location}.'}), 404
