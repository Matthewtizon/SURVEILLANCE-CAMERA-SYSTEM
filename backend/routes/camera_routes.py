# routes/camera_routes.py
from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from camera import get_frame_from_camera
import cv2
import logging

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify({'cameras': [{'camera_id': 0}]})  # Single camera

@camera_bp.route('/video_feed/<int:camera_id>', methods=['GET'])
def video_feed(camera_id):
    if camera_id != 0:
        return jsonify({"error": "Camera not found"}), 404
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while True:
        frame = get_frame_from_camera()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            logging.warning("Camera is not streaming any frame.")
            break
