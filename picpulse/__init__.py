from flask import Flask, current_app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy
from flask_cors import CORS
from flask_bcrypt import Bcrypt

logger = LocalProxy(lambda: current_app.logger)

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    Bcrypt(app)
    CORS(app)

    app.config.from_object('config.Config')

    login_manager.init_app(app)
    db.init_app(app)

    with app.app_context():
        from . import routes_auth, routes_user, routes_main
        
        app.register_blueprint(routes_auth.auth_bp)
        app.register_blueprint(routes_user.user_bp)
        app.register_blueprint(routes_main.main_bp)
        

    app.logger.info("Aplicació iniciada")

    return app