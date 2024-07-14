# routes/camera_routes.py
from flask import Blueprint, jsonify, Response
from models import Camera
import cv2

camera_bp = Blueprint('camera_bp', __name__)

