from flask import Flask, current_app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_principal import Principal
from werkzeug.local import LocalProxy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt

logger = LocalProxy(lambda: current_app.logger)

db_manager = SQLAlchemy()
login_manager = LoginManager()
principal_manager = Principal()

def create_app():
    app = Flask(__name__)
    Bcrypt(app)
    CORS(app, supports_credentials=True)


    app.config.from_object('config.Config')

    login_manager.init_app(app)
    db_manager.init_app(app)
    principal_manager.init_app(app)

    with app.app_context():
        from . import routes_main, routes_auth, routes_admin, routes_products
        app.register_blueprint(routes_main.main_bp)
        app.register_blueprint(routes_auth.auth_bp)
        app.register_blueprint(routes_admin.admin_bp)
        app.register_blueprint(routes_products.products_bp)

    app.logger.info("Aplicació iniciada")

    return app