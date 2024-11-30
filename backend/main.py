import logging
import signal
from gevent import monkey
from gevent.pywsgi import WSGIServer
from app import create_app, socketio
from models import User, Camera
from camera import camera_streams_dict, start_ip_camera
import threading
import os

# Declare http_server as a global variable
http_server = None

def signal_handler(signum, frame):
    logging.info("Signal received. Stopping the server...")
    http_server.stop()  # Stop the Gevent server
    exit(0)  # Exit the program

def initialize():
    app = create_app()
    socketio.init_app(app)

    with app.app_context():
        from db import db
        db.create_all()

        # Add default user if not exists
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt(app)
        if db.session.query(User).filter_by(username='Admin').count() < 1:
            hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
            new_user = User(username='Admin', password=hashed_password, role='Administrator', full_name='Admin', email='Admin@example.com', phone_number='+639774314024')
            db.session.add(new_user)
            db.session.commit()

        # Start active cameras
        active_cameras = Camera.query.filter_by(is_active=True).all()
        for camera in active_cameras:
            if camera.id not in camera_streams_dict:
                thread = threading.Thread(target=start_ip_camera, args=(app, camera.id, Camera, socketio))
                thread.start()
                camera_streams_dict[camera.id] = thread

    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        http_server = WSGIServer(('0.0.0.0', 5000), app)
        logging.info("Server is running on http://0.0.0.0:5000")
        http_server.serve_forever()
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")


if __name__ == '__main__':
    initialize()
