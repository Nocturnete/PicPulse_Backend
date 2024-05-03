from flask import Blueprint, request, jsonify, session, current_app
from . import db, logger
from flask_bcrypt import Bcrypt
from .models import User
from flask_httpauth import HTTPTokenAuth


auth_bp = Blueprint("auth_bp", __name__)
bcrypt = Bcrypt()
token_auth = HTTPTokenAuth()


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    userExist = User.query.filter_by(email=email).first()
    if userExist is None:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    if not bcrypt.check_password_hash(userExist.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = userExist.get_token()
    
    user_data = {
        # "id": userExist.id,
        "first_name": userExist.first_name,
        "last_name": userExist.last_name,
        "email": userExist.email,
        "role_id": userExist.role_id
    }

    print(user_data)
    current_app.logger.info("User logged in")
    return jsonify({"token": token, "user": user_data}), 200




@auth_bp.route("/register", methods=["POST"])
def register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json["email"]
    password = request.json["password"]
    role_id = 1 # Customer

    userExist = User.query.filter_by(email=email).first()
    if userExist:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    newUser = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role_id=role_id)
    db.session.add(newUser)
    db.session.commit()
    
    current_app.logger.info("USUARIO REGISTRADO")
    return jsonify({'mensaje': 'User created successfully!'})


@auth_bp.route("/logout", methods=["POST"])
@token_auth.login_required
def logout():
    token_auth.current_user().revoke_token()
    return jsonify({"message": "User logout successfully"}), 201


@token_auth.verify_token
def verify_token(token):
    current_app.logger.info(f"verify_token: {token}")
    return User.check_token(token)