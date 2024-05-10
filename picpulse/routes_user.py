from flask import Blueprint, jsonify, current_app, request, send_from_directory
from . import db, cross_origin
from .models import User, Profile, Album, Photo, Photo_improved
from .routes_auth import token_auth
from werkzeug.utils import secure_filename
import os



user_bp = Blueprint("user_bp", __name__)


# TODO LIST USERS
@cross_origin
@user_bp.route('/users', methods=['GET'])
@token_auth.login_required
def list_users():
    users = User.query.all()

    user_list = []

    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email,
            "role_name": user.role.name
        }

        user_list.append(user_data)

    current_app.logger.info("LISTA DE USUARIOS CARGADA")
    
    return jsonify(user_list)

# TODO VIEW USER
@cross_origin
@user_bp.route('/user/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    user_data = {
        "id": user_id,
        "name": user.name,
        "last_name": user.last_name,
        "email": user.email,
        "gender": profile.sexo,
        "phone": profile.phone
    }

    return jsonify(user_data)

# TODO UPDATE USER
@cross_origin
@user_bp.route("/user/update/<int:user_id>", methods=["PUT"])
@token_auth.login_required
def update_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    profile = Profile.query.filter_by(user_id=user_id).first()

    data = request.json
    if 'name' in data:
        user.name = data['name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        new_email = data['email']
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return jsonify({"message": "Email already exists"}), 400
        user.email = new_email
    if 'gender' in data:
        profile.gender = data['gender']
    if 'phone' in data:
        profile.phone = data['phone']
    
    db.session.commit()
    
    current_app.logger.info("USER UPDATED")
    return jsonify({"message": "User updated successfully", "user": user.serialize()}), 200

# TODO DELETE USER
@cross_origin
@user_bp.route("/user/delete/<int:user_id>", methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    photos = Photo.query.filter_by(user_id=user_id).all()
    for photo in photos:
        db.session.delete(photo)

    photos_improved = Photo_improved.query.join(Photo).filter(Photo.user_id == user_id).all()
    for photo_improved in photos_improved:
        db.session.delete(photo_improved)

    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        db.session.delete(profile)
    
    albums = Album.query.filter_by(user_id=user_id).all()
    for album in albums:
        db.session.delete(album)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200

# TODO PROFILE USER

@cross_origin
@user_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@token_auth.login_required
def handle_user_profile(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        profile = Profile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({"message": "Profile not found"}), 404

        profile_data = {
            "id": profile.id,
            "user_id": profile.user_id,
            "sexo": profile.sexo,
            "phone": profile.phone,
            "file_path": profile.file_path
        }

        return jsonify(profile_data)
        
    elif request.method == 'POST':
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "Profile not found"}), 404

        if 'image' not in request.files:
            return jsonify({"message": "No image provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"message": "No selected image"}), 400

        if image_file:
            user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], user.email)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            filename = secure_filename(image_file.filename)
            image_path = os.path.join(user_folder, filename)
            image_file.save(image_path)

            profile.file_path = os.path.join(user.email, filename)
            print("PROFILEEEEEEE", profile.file_path)
            db.session.commit()
            return jsonify({"message": "Image uploaded successfully"}), 200
        
        else:
            return jsonify({"message": "Failed to upload image"}), 400