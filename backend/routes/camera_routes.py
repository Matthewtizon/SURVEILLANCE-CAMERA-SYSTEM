# routes/camera_routes.py
from flask import Blueprint, jsonify, request, Response, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import Camera
import logging
from camera import camera_threads  # Adjust import to use camera_threads from camera.py
from app import socketio  # Import socketio instance from app.py

camera_bp = Blueprint('camera_bp', __name__)
logger = logging.getLogger(__name__)

@camera_bp.route('/camera-stream')
@jwt_required()
def camera_stream():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while True:
        for camera_location, queue in camera_threads.items():  # Use camera_threads here
            frame = queue.get()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
