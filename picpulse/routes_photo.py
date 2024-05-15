from flask import Blueprint, request, jsonify, current_app, g, send_from_directory
from werkzeug.utils import secure_filename
from . import db, cross_origin
from .models import Photo, Photo_improved
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

    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H')
        unique_filename = f"{now}_{filename}"
        folder_name = f"{user_id}"
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, unique_filename)

        try:
            file.save(file_path)

            new_photo_improved = Photo_improved(
                name=filename,
                path=file_path,
                size=os.path.getsize(file_path),
                format=file_path.rsplit('.', 1)[1],
                user_id=user_id
            )

            db.session.add(new_photo_improved)
            db.session.commit()

            return jsonify({'message': 'La foto mejorada se ha guardado correctamente'}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    else:
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400





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
