from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import Camera
from camera import camera_queues
import cv2

camera_bp = Blueprint('camera_bp', __name__)

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
        return jsonify({'message': 'Token is invalid or expired'}), 401

    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403
    
    def generate():
        queue = camera_queues.get(camera_location)
        if queue is None:
            return Response("Error: Camera not found", status=404)

        while True:
            frame = queue.get()
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
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
