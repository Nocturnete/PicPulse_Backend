from flask import Blueprint, request, jsonify, current_app
from . import db, cross_origin
from flask_bcrypt import Bcrypt
from .models import User
from flask_httpauth import HTTPTokenAuth


auth_bp = Blueprint("auth_bp", __name__)

bcrypt = Bcrypt()
token_auth = HTTPTokenAuth(scheme='Bearer')


# TODO REGISTER
@cross_origin
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get('name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    role_id = 1 # Customer

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists!'}), 400

    hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
    
    newUser = User(name=name, last_name=last_name, email=email, password=hashedPassword, role_id=role_id)
    db.session.add(newUser)
    db.session.commit()
    
    current_app.logger.info("USER REGISTERED")
    return jsonify({'message': 'User registered successfully!'}), 201

# TODO LOGIN
@cross_origin
@auth_bp.route("/signin", methods=["POST"])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        token = user.get_token()

        current_app.logger.info("LOGIN SUCCESSFUL")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'name': user.name,
            'last_name': user.last_name,
            'role_id': user.role_id
        }), 200
    
    else:
        current_app.logger.info("INVALID USER")
        return jsonify({'message': 'Invalid email or password'}), 401

@cross_origin
@token_auth.verify_token
def verify_token(token):
    current_app.logger.info(f"verify_token: {token}")
    return User.check_token(token)

# TODO LOGOUT
@cross_origin
@auth_bp.route("/logout", methods=["POST"])
@token_auth.login_required
def logout():
    token_auth.current_user().revoke_token()
    return jsonify({"message": "User logout successfully"}), 201
