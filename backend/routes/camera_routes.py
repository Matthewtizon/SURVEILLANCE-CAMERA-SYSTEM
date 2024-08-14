from flask import Blueprint, jsonify, Response, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from camera import get_frame_from_camera
import logging
import cv2

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['Administrator', 'Assistant Administrator', 'Security Staff']:
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify({'cameras': [{'camera_id': 0}]})

@camera_bp.route('/video_feed/<int:camera_id>', methods=['GET'])
def video_feed(camera_id):
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is missing"}), 401
    
    # Manually set the JWT in the request header
    request.headers = {"Authorization": f"Bearer {token}"}

    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user['role'] not in ['Administrator', 'Assistant Administrator', 'Security Staff']:
            return jsonify({'message': 'Unauthorized'}), 403
    except Exception as e:
        logging.error(f"JWT Error: {e}")
        return jsonify({"error": "Invalid token"}), 401

    if camera_id != 0:
        return jsonify({"error": "Camera not found"}), 404
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while True:
        try:
            frame = get_frame_from_camera()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                logging.warning("No frame received from camera.")
                break
        except Exception as e:
            logging.error(f"Error streaming frames: {e}")
            break
