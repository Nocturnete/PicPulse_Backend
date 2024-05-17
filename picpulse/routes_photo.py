from flask import Blueprint, jsonify, current_app, request, send_from_directory
from . import db, cross_origin
from .models import User, Profile, Album, Photo, Photo_improved
from .routes_auth import token_auth
from werkzeug.utils import secure_filename
import os


photo_bp = Blueprint("photo_bp", __name__)


# TODO LIST HQ PHOTOS
@cross_origin
@photo_bp.route('/photos/community', methods=['GET'])
def get_photos():
    uploads_folder = os.path.join(current_app.root_path, 'uploads')
    hq_images = []

    for root, dirs, files in os.walk(uploads_folder):
        for file in files:
            if file.startswith("HQ_"):
                relative_path = os.path.relpath(os.path.join(root, file), current_app.root_path)
                hq_images.append(relative_path)

    return jsonify(hq_images), 200


# TODO GET IMAGE COMUNITY
@cross_origin
@photo_bp.route('/get_image/<path:filepath>', methods=['GET'])
def serve_photo(filepath):
    return send_from_directory(os.path.join(current_app.root_path), filepath)
