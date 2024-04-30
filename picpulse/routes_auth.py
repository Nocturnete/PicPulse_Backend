from flask import Blueprint, request, jsonify, current_app, make_response, session
from flask_login import login_required, login_user, logout_user
from . import db_manager as db, login_manager, logger
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from datetime import datetime, timedelta
import secrets
import jwt
from flask_bcrypt import Bcrypt


# Blueprint
auth_bp = Blueprint("auth_bp", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized Access"}), 401
  
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
      
    token = secrets.token_urlsafe(20)
  
    session['token'] = token

    return jsonify({'token': token}), 200



@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json["email"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
 
    session["user_id"] = new_user.id
 
    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })


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
