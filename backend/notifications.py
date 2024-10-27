import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize the Boto3 SNS client
sns_client = boto3.client(
    'sns',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")  # e.g., 'us-west-2'
)

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")  # Add your SNS topic ARN here

def send_notification(url):
    now = datetime.now()
    formatted_now = now.strftime("%d/%m/%y %H:%M:%S")
    message = f"Unknown face detected @{formatted_now} - {url}"

    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="Alert: Unknown Face Detected"
    )
    print("Notification sent:", response)
