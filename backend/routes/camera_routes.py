# camera_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import Camera
from camera import camera_queues
from flask_socketio import emit
import cv2
from threading import Lock, Thread
from socketio_instance import socketio
from functools import wraps
import jwt

camera_bp = Blueprint('camera_bp', __name__)
thread_lock = Lock()

# Mock secret for JWT decoding (use your actual secret)
SECRET_KEY = 'your_secret_key'

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')  # get token from query parameter

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated_function

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = Camera.query.all()
    unique_cameras = {camera.location: camera for camera in cameras}.values()  # Remove duplicates based on location
    camera_list = [{"camera_id": camera.camera_id, "location": camera.location} for camera in unique_cameras]
    return jsonify(camera_list), 200

@camera_bp.route('/camera_feed/<string:camera_location>', methods=['GET'])
@token_required
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
            print(f"Emitting frame for {camera_location}")  # Debug statement
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
