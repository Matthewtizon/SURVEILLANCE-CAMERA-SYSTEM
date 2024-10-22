import firebase_admin
from firebase_admin import credentials, messaging
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Firebase Admin SDK with your service account
cred = credentials.Certificate("surveillance-camera-push-notif.json")
firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        logging.info('Successfully sent message: %s', response)
    except Exception as e:
        logging.error('Error sending message: %s', e)