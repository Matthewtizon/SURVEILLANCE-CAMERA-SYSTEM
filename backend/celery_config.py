from celery import Celery

# Create the Celery app
app = Celery('tasks', broker='redis://localhost:6379/0')

# Optional: Configure Celery
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks to register them with the Celery app
import tasks  # Ensure this is the correct module name where your tasks are defined
