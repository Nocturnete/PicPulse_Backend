from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt


logger = LocalProxy(lambda: current_app.logger)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config.from_object('config.Config')

    app.logger.info("Database: " + app.config['SQLALCHEMY_DATABASE_URI'])

    CORS(app)
    db.init_app(app)


    with app.app_context():
        from . import routes_auth, routes_user

        app.register_blueprint(routes_auth.auth_bp)
        app.register_blueprint(routes_user.user_bp)

    
    app.logger.info("Aplicació iniciada")

    return app