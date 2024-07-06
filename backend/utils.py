# backend/utils.py
from flask import current_app

def with_app_context(func):
    def wrapper(*args, **kwargs):
        with current_app.app_context():
            return func(*args, **kwargs)
    return wrapper
