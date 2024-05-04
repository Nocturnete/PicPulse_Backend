from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
from sqlalchemy.sql import func
from uuid import uuid4
from . import db
import secrets
from .mixins import BaseMixin


def get_uuid():
    return uuid4().hex

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    path = db.Column(db.String(255), nullable=False)
    
    user = db.relationship('User', backref='profiles')


class User(db.Model, BaseMixin, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    token = db.Column(db.String(255), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.first_name}>'

    def get_token(self, expires_in=70):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration:
            token_expiration_naive = self.token_expiration.replace(tzinfo=None)
            now_naive = now.replace(tzinfo=None)
            if token_expiration_naive > now_naive + timedelta(seconds=30):
                return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.commit()
        return self.token
    
    def revoke_token(self):
        self.token_expiration = None
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or (user.token_expiration and user.token_expiration < datetime.now(timezone.utc).replace(tzinfo=None)):
            return None
        return user
    


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

