# models.py
from db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)


class VideoDeletionAudit(db.Model):
    __tablename__ = 'video_deletion_audit'
    
    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(255), nullable=False)
    deleted_by = db.Column(db.String(255), nullable=False)  # Username or user ID
    deleted_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, video_name, deleted_by):
        self.video_name = video_name
        self.deleted_by = deleted_by