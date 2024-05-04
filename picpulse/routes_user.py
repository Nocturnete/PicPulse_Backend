from flask import Blueprint, jsonify, current_app
from . import db, logger
from .models import User
from .routes_auth import token_auth


user_bp = Blueprint("user_bp", __name__)


# TODO Ruta para obtener todos los usuarios
@user_bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    users = User.query.all()

    user_list = [{
        "id": user.id, 
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role_name": user.role.name} for user in users]
    
    current_app.logger.info("LISTA DE USUARIOS CARGADA")

    return jsonify(user_list), 200


# TODO Ruta para obtener un usuario por ID
@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)

    if user:
        user_data = {
            "id": user.id, 
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role_id": user.role.name
        }

        current_app.logger.info("DATOS DEL USUARIO CARGADOS")

        return jsonify(user_data), 200
    
    else:
        current_app.logger.info("DATOS DEL USUARIO NO ENCONTRADOS")

        return jsonify({"message": "User not found"}), 404
    

# TODO Ruta para eliminar un usuario
@user_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        
        current_app.logger.info("USUARIO ELIMINADO")

        return jsonify({"message": "User deleted successfully"}), 200
    
    else:
        current_app.logger.info("NO SE HA PODIDO ELIMINAR EL USUARIO")

        return jsonify({"message": "User not found"}), 404