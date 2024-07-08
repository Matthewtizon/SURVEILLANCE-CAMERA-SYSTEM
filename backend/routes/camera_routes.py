from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import Camera
from camera import camera_queues
from flask_socketio import emit
import cv2
from threading import Lock, Thread
from socketio_instance import socketio  # Import socketio instance

camera_bp = Blueprint('camera_bp', __name__)
thread_lock = Lock()

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = Camera.query.all()
    camera_list = [{"camera_id": camera.camera_id, "location": camera.location} for camera in cameras]
    return jsonify(camera_list), 200

@camera_bp.route('/camera_feed/<string:camera_location>', methods=['GET'])
@jwt_required()
def camera_feed(camera_location):
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded_token = decode_token(token)
        current_user = decoded_token['sub']
    except Exception as e:
        print(f"Token error: {e}")
        return jsonify({'message': 'Token is invalid or expired'}), 401

    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    return emit_camera_feed(camera_location)

def emit_camera_feed(camera_location):
    queue = camera_queues.get(camera_location)
    if queue is None:
        return jsonify({'message': 'Camera not found'}), 404

    def emit_frames():
        while True:
            frame = queue.get()
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                jpeg_bytes = jpeg.tobytes()
                socketio.emit('camera_frame', {'image': True, 'data': jpeg_bytes, 'cameraLocation': camera_location}, namespace='/')
            else:
                print("Error encoding frame")

    if not thread_lock.locked():
        with thread_lock:
            thread = Thread(target=emit_frames)
            thread.daemon = True
            thread.start()

    return jsonify({'message': 'Streaming started'}), 200
