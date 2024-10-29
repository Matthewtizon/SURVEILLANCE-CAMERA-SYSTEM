# config.py
import os


sms_notifications_enabled = True

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:johnmatthew300@localhost:3306/surveillance_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'