from flask import Blueprint, jsonify, current_app, request
from . import cross_origin
from .models import User, Profile
from .routes_auth import token_auth


user_bp = Blueprint("user_bp", __name__)


# TODO Lista usuarios
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

# TODO Profile
@cross_origin
@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            profile_data = {
                "id": profile.id,
                "user_id": profile.user_id,
                "sexo": profile.sexo,
                "phone": profile.phone,
                "file_path": profile.file_path
            }
            return jsonify(profile_data)
        else:
            return jsonify({"message": "Profile not found"}), 404
    else:
        return jsonify({"message": "User not found"}), 404