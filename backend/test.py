from app import create_app, db
from models import Camera


camera = Camera.query.get(1)
print(camera)
