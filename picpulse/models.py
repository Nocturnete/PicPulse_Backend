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


class Model(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)


class User(db.Model, BaseMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, server_default=func.now())

    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.name}>'
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration:
            token_expiration_naive = self.token_expiration.replace(tzinfo=None)
            now_naive = now.replace(tzinfo=None)
            if token_expiration_naive > now_naive:
                print("Token aún válido. No se genera uno nuevo.")
                return self.token

        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=3600)
        db.session.add(self)
        db.session.commit()
        print("Se ha generado un nuevo token.")
        print("El token expirará en:", self.token_expiration)
        return self.token
    
    def revoke_token(self):
        self.token = None
        self.token_expiration = None
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or (user.token_expiration and user.token_expiration < datetime.now(timezone.utc).replace(tzinfo=None)):
            return None
        return user

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
        }


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='albums')


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gender = db.Column(db.String(255))
    phone = db.Column(db.Integer)
    file_path = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='profiles')


class Photo_improved(db.Model):
    __tablename__ = "photos_improved"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(25), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
    created_at = db.Column(db.DateTime, server_default=func.now())

    user = db.relationship('User', backref='photos_improved')
    model = db.relationship('Model', backref='photos_improved')
    album = db.relationship('Album', backref='photos_improved')

    def __repr__(self):
        return '<PhotoImproved {}>'.format(self.id)


class Photo(db.Model):
    __tablename__ = "photos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(25), nullable=False)
    photo_improved_id = db.Column(db.Integer, db.ForeignKey('photos_improved.id')) 
    created_at = db.Column(db.DateTime, server_default=func.now())
    
    photo_improved = db.relationship('Photo_improved', backref='photos')



    
