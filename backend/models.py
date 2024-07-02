# models.py
from db import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Camera(db.Model):
    camera_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
