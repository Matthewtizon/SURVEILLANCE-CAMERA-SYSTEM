from flask import Blueprint, jsonify, current_app as app
from models import Camera
from db import db
from camera import camera_queues, frame_data, start_frame_thread
import base64
import cv2

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/cameras', methods=['GET'])
def get_cameras():
    cameras = Camera.query.all()
    camera_list = [{'id': camera.id, 'location': camera.location} for camera in cameras]
    return jsonify(camera_list)

@camera_bp.route('/camera/<int:id>', methods=['GET'])
def get_camera(id):
    camera = Camera.query.get_or_404(id)
    return jsonify({'id': camera.id, 'location': camera.location})

@camera_bp.route('/start_stream/<int:id>', methods=['GET'])
def start_camera_stream(id):
    camera = Camera.query.get_or_404(id)
    camera_location = camera.location
    if camera_location in camera_queues:
        # Start a new thread to emit frames for this camera
        thread = start_frame_thread(camera_location)
        return jsonify({'message': f'Started streaming for camera {id} at {camera_location}.'})
    else:
        return jsonify({'error': f'Camera {id} at {camera_location} is not available.'}), 404

@camera_bp.route('/stop_stream/<int:id>', methods=['GET'])
def stop_camera_stream(id):
    camera = Camera.query.get_or_404(id)
    camera_location = camera.location
    # Implement logic to stop the streaming thread if needed
    return jsonify({'message': f'Stopped streaming for camera {id} at {camera_location}.'})

@camera_bp.route('/latest_frame/<int:id>', methods=['GET'])
def get_latest_frame(id):
    camera = Camera.query.get_or_404(id)
    camera_location = camera.location
    if camera_location in frame_data:
        latest_frame = frame_data[camera_location]
        return jsonify({'frame': latest_frame})
    else:
        return jsonify({'error': f'No frame available for camera {id} at {camera_location}.'}), 404

@camera_bp.route('/all_frames', methods=['GET'])
def get_all_frames():
    serializable_frames = {}
    for camera_location, frame in frame_data.items():
        # Convert frame ndarray to a serializable format, like base64
        frame_encoded = cv2.imencode('.jpg', frame)[1].tobytes()
        frame_base64 = base64.b64encode(frame_encoded).decode('utf-8')
        serializable_frames[camera_location] = frame_base64

    return jsonify(serializable_frames)

@camera_bp.route('/clear_frames', methods=['GET'])
def clear_all_frames():
    global frame_data
    frame_data = {}
    return jsonify({'message': 'Cleared all frame data.'})

@camera_bp.route('/camera_status', methods=['GET'])
def get_camera_status():
    return jsonify({'camera_queues': list(camera_queues.keys()), 'frame_data_keys': list(frame_data.keys())})