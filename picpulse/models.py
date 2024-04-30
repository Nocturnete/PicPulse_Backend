from flask_login import UserMixin
from . import db_manager as db
from sqlalchemy.sql import func
from uuid import uuid4


def get_uuid():
    return uuid4().hex

class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    token = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return self.email
    
    def is_admin(self):
        return self.role == "admin"

    def is_ia(self):
        return self.role == "IA"
    
    def is_admin_or_moderator(self):
        return self.is_admin()
    
    def is_customer(self):
        return self.role == "customer"

    def is_action_allowed_to_product(self, action, product = None):
        from .helper_role import _permissions, Action

        current_permissions = _permissions[self.role]
        if not current_permissions:
            return False
        
        if not action in current_permissions:
            return False
        
        # Un usuari wanner sols pot modificar el seu propi producte
        if (action == Action.products_update and self.is_customer()):
            if not product:
                return False
            return self.id == product.seller_id
        
        # Un usuari wanner sols pot eliminar el seu propi producte
        if (action == Action.products_delete and self.is_customer()):
            if not product:
                return False
            return self.id == product.seller_id
        
        # si hem arribat fins aquí, l'usuari té permisos
        return True

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now())
    updated = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Photo(db.Model):
    __tablename__ = "photos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(25), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

class Model(db.Model):
    __tablename__ = "models"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String, nullable=False)
    path = db.Column(db.String(255), nullable=False)

class Photo_improved(db.Model):
    __tablename__ = "photos_improved"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(25), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
