from flask_socketio import SocketIO

# Ensure that logging is enabled for debugging purposes
import logging
logging.basicConfig(level=logging.DEBUG)

# Create SocketIO instance with proper CORS configuration
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)