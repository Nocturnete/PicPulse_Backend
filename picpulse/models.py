from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func
from uuid import uuid4


def get_uuid():
    return uuid4().hex

class Role(db.Model):
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

    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.first_name}>'

class Photo(db.Model):
    __tablename__ = "photos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(25), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    user = db.relationship('User', backref='photos')

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

    model = db.relationship('Model', backref='photos_improved')
    photo = db.relationship('Photo', backref='photos_improved')

