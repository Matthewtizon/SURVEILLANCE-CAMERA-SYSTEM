# routes/camera_routes.py
from flask import Blueprint, jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
import cv2
import imutils
from models import Camera
from db import db

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/camera_feed/<int:camera_id>')
def camera_feed(camera_id):
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded_token = decode_token(token)
        current_user = decoded_token['sub']
    except Exception as e:
        return jsonify({'message': 'Token is invalid or expired'}), 401

    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    @stream_with_context
    def generate():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error opening video stream or file"

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = imutils.resize(frame, width=400)  # Adjust frame size if needed
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = Camera.query.all()
    camera_list = [{"camera_id": camera.camera_id, "location": camera.location} for camera in cameras]
    return jsonify(camera_list), 200

@camera_bp.route('/detect_cameras', methods=['POST'])
@jwt_required()
def detect_and_save_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = detect_cameras()
    for cam in cameras:
        existing_camera = Camera.query.filter_by(camera_id=cam["camera_id"]).first()
        if not existing_camera:
            new_camera = Camera(camera_id=cam["camera_id"], location=cam["location"])
            db.session.add(new_camera)
            db.session.commit()
    return jsonify({'message': 'Cameras detected and saved successfully!'}), 200
