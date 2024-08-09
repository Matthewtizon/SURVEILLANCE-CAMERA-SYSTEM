# routes/camera_routes.py
from flask import Blueprint, jsonify, Response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from camera import camera_queues, get_frame_from_camera, max_ports
import cv2
import logging

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403
    cameras = [{'camera_id': camera_id} for camera_id in camera_queues.keys()]
    return jsonify({'cameras': cameras if cameras else []}), 200

@camera_bp.route('/video_feed/<int:camera_id>', methods=['GET'])
def video_feed(camera_id):
    if camera_id not in camera_queues:
        return jsonify({"error": "Camera not found"}), 404
    return Response(gen_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames(camera_id):
    while True:
        frame = get_frame_from_camera(camera_id)
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            logging.warning(f"Camera {camera_id} is not streaming any frame.")
            break

@camera_bp.route('/camera_status', methods=['GET'])
def camera_status():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    # Here, you might want to validate the token, depending on your authentication setup

    status = []
    for i in range(max_ports):
        if i in camera_queues:
            status.append({'port': i, 'occupied': True})
        else:
            status.append({'port': i, 'occupied': False})
    return jsonify(status)
