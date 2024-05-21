from flask import Blueprint, jsonify, current_app, request, send_from_directory
from . import db, cross_origin
from .models import User, Profile, Album, Photo, Photo_improved
from .routes_auth import token_auth
from werkzeug.utils import secure_filename
import os


album_bp = Blueprint("album_bp", __name__)


# TODO LIST HQ PHOTOS
@cross_origin
@album_bp.route('/album/<userid>', methods=['GET'])
@token_auth.login_required
def get_photos(userid):
    uploads_folder = os.path.join(current_app.root_path, 'uploads', userid)
    hq_images = []

    if not os.path.exists(uploads_folder):
        return jsonify({"error": "User uploads folder does not exist"}), 404

    for root, dirs, files in os.walk(uploads_folder):
        for file in files:
            if file.startswith("HQ_"):
                relative_path = os.path.relpath(os.path.join(root, file), current_app.root_path)
                hq_images.append(relative_path)

    return jsonify(hq_images), 200
