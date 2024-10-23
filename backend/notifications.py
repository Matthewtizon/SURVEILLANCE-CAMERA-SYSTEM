import firebase_admin
from firebase_admin import messaging

# Initialize FCM
if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate('surveillance-camera-push-notif.json')
    firebase_admin.initialize_app(cred)

def send_notification(device_token, message):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title='Notification Title',
                body=message,
            ),
            token=device_token,
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except messaging.FirebaseError as e:
        print('Error sending message:', e)