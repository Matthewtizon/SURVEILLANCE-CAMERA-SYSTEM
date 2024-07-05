# routes/camera_routes.py
from flask import Blueprint, jsonify, request, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import Camera
from camera import generate_camera_feed

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
    
    def generate_feed():
        for frame in generate_camera_feed(camera_id):
            yield frame

    return Response(generate_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403

    cameras = Camera.query.all()
    camera_list = [{"camera_id": camera.camera_id, "location": camera.location} for camera in cameras]
    return jsonify(camera_list), 200
