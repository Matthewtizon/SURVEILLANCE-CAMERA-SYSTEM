from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Camera
from camera import start_camera_stream, start_camera, camera_streams_dict, camera_streams
import threading
import datetime
from storage import list_videos_in_date_range, bucket
from urllib.parse import unquote
from models import  VideoDeletionAudit, Camera
from db import db
import logging
from flask_cors import cross_origin
from alert import check_alert
from face_recognition import recognize_faces


def create_camera_routes(app, socketio):
    camera_bp = Blueprint('camera', __name__)





    @camera_bp.route('/api/get_recorded_videos', methods=['GET'])
    @jwt_required()
    def get_recorded_videos():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            today = datetime.datetime.now()
            start_date = today.strftime('%Y-%m-%d')  # Start of today
            end_date = today.strftime('%Y-%m-%d')    # End of today

        # Validate date formats
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

        videos = list_videos_in_date_range(start_date, end_date)
        
        if not videos:
            return jsonify({"message": "No videos found for the selected date range."}), 404

        return jsonify(videos), 200

    @camera_bp.route('/api/delete_video', methods=['DELETE'])
    @jwt_required()
    def delete_video():
        video_url = request.args.get('url')

        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        try:
            # Decode the URL
            decoded_url = unquote(video_url)
            
            # Extract the blob name from the decoded URL
            blob_name = decoded_url.split('/')[-1]

            # Delete the video from the bucket
            blob = bucket.blob(blob_name)
            
            # Check if the blob exists before trying to delete it
            if not blob.exists():
                return jsonify({"error": f"Video {blob_name} does not exist."}), 404

            # Delete the video
            blob.delete()
            
            # Log the deletion in the audit trail
            deleted_by = get_jwt_identity()  # Get the user identity from the JWT
            audit_entry = VideoDeletionAudit(video_name=blob_name, deleted_by=deleted_by)
            db.session.add(audit_entry)
            db.session.commit()

            return jsonify({"message": f"Video {blob_name} deleted successfully."}), 200
            
        except Exception as e:
            logging.error(f"Error deleting video: {str(e)}")
            return jsonify({"error": str(e)}), 500
        

    @camera_bp.route('/api/video_audit_trail', methods=['GET'])
    @jwt_required()  # Ensure the user is authenticated
    def get_audit_trail():
        try:
            # Query the audit trail data from the database
            audit_trails = VideoDeletionAudit.query.all()
            
            # Format the results
            audit_data = [
                {
                    "id": audit.id,
                    "video_name": audit.video_name,
                    "deleted_by": audit.deleted_by,
                    "deleted_at": audit.deleted_at.isoformat()  # Convert to ISO format
                }
                for audit in audit_trails
            ]

            return jsonify(audit_data), 200
        except Exception as e:
            logging.error(f"Error fetching audit trail: {str(e)}")
            return jsonify({"error": "Unable to fetch audit trail data."}), 500

    @camera_bp.route('/api/cameras', methods=['GET'])
    @jwt_required()
    def get_cameras():
        cameras = Camera.query.all()
        cameras_data = [
            {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "is_active": camera.is_active
            }
            for camera in cameras
        ]
        return jsonify(cameras_data), 200


    @camera_bp.route('/api/cameras', methods=['POST'])
    @jwt_required()
    def add_camera():
        data = request.get_json()

        # Create new Camera object
        new_camera = Camera(name=data['name'], rtsp_url=data['rtsp_url'], is_active=True)
        
        # Add to the database
        db.session.add(new_camera)
        db.session.commit()

        print(f"Starting thread with args: {new_camera.id}")
        thread = threading.Thread(target=start_camera_stream, args=(app, new_camera.id))
        thread.start()
        camera_streams_dict[new_camera.id] = thread

        return jsonify({"message": "Camera added and streaming started", "camera": {
            "id": new_camera.id,
            "name": new_camera.name,
            "rtsp_url": new_camera.rtsp_url,
            "is_active": new_camera.is_active
        }}), 201

    # Flask routes to update and delete cameras

    @camera_bp.route('/api/cameras/<int:camera_id>', methods=['PUT'])
    @jwt_required()
    @cross_origin(origins='http://10.242.104.90', methods=["GET", "POST", "PUT", "DELETE"])
    def update_camera(camera_id):
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({"error": "Camera not found"}), 404

        data = request.get_json()
        camera.name = data.get('name', camera.name)
        #camera.rtsp_url = data.get('rtsp_url', camera.rtsp_url)
        db.session.commit()

        return jsonify({"message": "Camera updated successfully", "camera": {
            "id": camera.id,
            "name": camera.name,
            "rtsp_url": camera.rtsp_url,
            "is_active": camera.is_active
        }}), 200

    @camera_bp.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
    @jwt_required()
    def delete_camera(camera_id):
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({"error": "Camera not found"}), 404

        # Stop the stream if the camera is active
        if camera.is_active:
            camera_streams_dict.pop(camera_id, None)  # Remove the camera stream from dictionary

        db.session.delete(camera)
        db.session.commit()
        return jsonify({"message": "Camera deleted successfully"}), 200

    @camera_bp.route('/api/open_camera/<camera_ip>', methods=['GET'])
    @jwt_required()
    def open_camera(camera_ip):
        if camera_ip not in camera_streams:
            thread = threading.Thread(target=start_camera, args=(camera_ip, camera_streams, recognize_faces, check_alert, socketio))

            thread.start()
            camera_streams[camera_ip] = thread

            # Emit event to notify all clients about the change in camera status
            socketio.emit('camera_status_changed', {'camera_ip': camera_ip, 'status': 'opened'})

            return jsonify({'message': f'Camera {camera_ip} started'}), 200
        return jsonify({'message': f'Camera {camera_ip} is already running'}), 400

    @camera_bp.route('/api/close_camera/<camera_ip>', methods=['GET'])
    @jwt_required()
    def close_camera(camera_ip):
        if camera_ip in camera_streams:
            del camera_streams[camera_ip]

            # Emit event to notify all clients about the change in camera status
            socketio.emit('camera_status_changed', {'camera_ip': camera_ip, 'status': 'closed'})

            return jsonify({'message': f'Camera {camera_ip} stopped'}), 200
        return jsonify({'message': f'Camera {camera_ip} is not running'}), 400


    # Add this route in app.py to get the status of all cameras
    @camera_bp.route('/api/camera_status', methods=['GET'])
    @jwt_required()
    def camera_status():
        camera_status_dict = {camera_ip: True for camera_ip in camera_streams.keys()}
        return jsonify(camera_status_dict), 200
    
    return camera_bp