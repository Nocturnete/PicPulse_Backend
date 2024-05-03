from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, login_user, logout_user
from . import db, login_manager, logger
from flask_bcrypt import Bcrypt
from .models import User
import secrets


auth_bp = Blueprint("auth_bp", __name__)
bcrypt = Bcrypt()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    userExist = User.query.filter_by(email=email).first()
    print(userExist)
    if userExist is None:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    if not bcrypt.check_password_hash(userExist.password, password):
        return jsonify({"error": "Unauthorized"}), 401
      
    token = secrets.token_urlsafe(20)
  
    session['token'] = token

    current_app.logger.info("HA INICIADO SESIÓN")

    return jsonify({'token': token}), 200




@auth_bp.route("/register", methods=["GET", "POST"])
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
 
    session["user_id"] = newUser.id
 
    
    current_app.logger.info("USUARIO REGISTRADO")

    return jsonify({ "id": newUser.id, "email": newUser.email })




@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User logout successfully"}), 201


@login_manager.user_loader
def load_user(email):
    if email is not None:
        return db.session.query(User).filter(User.email == email).one_or_none()
    return None


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authenticate or register to access this page"}), 401
