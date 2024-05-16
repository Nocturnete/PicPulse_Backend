from flask import Blueprint, jsonify, request, current_app, g, send_from_directory
from .models import Photo, Photo_improved, Album
from werkzeug.utils import secure_filename
from .routes_auth import token_auth
from sqlalchemy.sql import func
from . import db, cross_origin
import picpulse.SR as arch
import numpy as np
import datetime
import torch
import cv2
import os


ia_bp = Blueprint('ia_bp', __name__)


device = torch.device('cpu')

model_path = 'picpulse/models/HighQuality.pth'
model = arch.RRDBNet(3, 3, 64, 23, gc=32)
model.load_state_dict(torch.load(model_path, map_location=device), strict=False)
model.eval()
model = model.to(device) 


# TODO ALLOWED EXTENSION
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS')


# TODO SAVE AND IMPROVE IMAGE
@ia_bp.route('/process_image', methods=['POST'])
@token_auth.login_required
def process_image():
    user_id = g.current_user.id

    image_file = request.files['image']

    if 'image' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    if image_file.filename == '':
        return jsonify({'error': 'No se ha proporcionado ninguna imagen'}), 400

    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H')
        unique_filename = f"{now}_{filename}"

        folder_name = f"{user_id}"
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filepath = os.path.join(folder_path, unique_filename)
        
        image_file.save(filepath)

        try:
            photo = Photo(
                name = unique_filename,
                path = filepath,
                size = os.path.getsize(filepath),
                format = filename.rsplit('.', 1)[1].lower(),
                photo_improved_id = None,
                created_at = func.now()
            )
            
            db.session.add(photo)
            db.session.commit()

            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            img = img * 1.0 / 255
            img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
            img_LR = img.unsqueeze(0)
            img_LR = img_LR.to(device)

            with torch.no_grad():
                output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()

            output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
            output = (output * 255.0).round()

            processed_image_name = "HQ_" + unique_filename
            processed_image_path =  os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name, processed_image_name)

            cv2.imwrite(processed_image_path, output)
            
            album = Album.query.filter_by(user_id=user_id).first()
            album_id = album.id

            image_path = "uploads/" + folder_name + "/" + processed_image_name
            # print ("***************************************************************")
            # print ("RUTA NUEVA: ", image_path)
            # print ("***************************************************************")

            photo_improved = Photo_improved(
                name = processed_image_name,
                path = image_path,
                size = os.path.getsize(processed_image_path),
                format = filename.rsplit('.', 1)[1].lower(),
                user_id = user_id,
                model_id = 1,
                album_id = album_id,
                created_at = func.now()
            )

            db.session.add(photo_improved)
            db.session.commit()

            photo.photo_improved_id = photo_improved.id
            db.session.commit()

            return jsonify({'message': 'Imagen procesada exitosamente', 'processed_image_path': processed_image_path , 'id': photo_improved.id})

        except Exception as e:
            return jsonify({'error': 'Error al procesar la imagen', 'details': str(e)}), 500


# TODO VIEW IMAGE
@cross_origin
@ia_bp.route('/get_processed_image/<int:photo_improved_id>', methods=['GET'])
@token_auth.login_required
def get_processed_image(photo_improved_id):
    photo_improved = Photo_improved.query.get(photo_improved_id)

    if photo_improved:
        directory = os.path.join(current_app.root_path)
        filename = os.path.join(photo_improved.path)
        # print("RUTA : ", directory)
        # print("BD : ", filename)
        
        return send_from_directory(directory, filename)
    
    else:
        return jsonify({'error': 'La imagen no existe'}), 404