from flask import Blueprint, request, jsonify, current_app, g, send_from_directory
from werkzeug.utils import secure_filename
from . import db, cross_origin
from .models import Photo
from .routes_auth import token_auth
import os
from sqlalchemy.sql import func
import datetime


photo_bp = Blueprint("photo_bp", __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS')


# TODO CREATE PHOTO
@cross_origin
@photo_bp.route('/photo/create', methods=['POST'])
@token_auth.login_required
def create_photo():
    user_id = g.current_user.id
    # print("USER ID: ", user_id)

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        unique_filename = f"{now}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        photo = Photo(
            user_id=user_id,
            path=filepath,
            size=os.path.getsize(filepath),
            format=filename.rsplit('.', 1)[1].lower(),
            created_at=func.now()
        )
        
        db.session.add(photo)
        db.session.commit()

        return jsonify({"message": "Photo uploaded successfully", "photo_id": photo.id}), 201

    return jsonify({"error": "Invalid file type"}), 400


# TODO GRID PHOTO
@cross_origin
@photo_bp.route('/photos', methods=['GET'])
def photo_grid():
    photo_folder = os.path.join(current_app.root_path, 'uploads')
    # print("PHOTOS FOLDER", photo_folder)
    photos = os.listdir(photo_folder)
    # print("PHOTOS LIST", photos)
    photo_urls = [f'/uploads/{photo}' for photo in photos]
    # print("URLS PHOTOS", photo_urls)
    current_app.logger.info("LISTA DE FOTOS CARGADA")
    return jsonify(images=photo_urls), 200


@cross_origin
@photo_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_photo(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), filename)
