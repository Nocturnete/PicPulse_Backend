from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
    
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_MYSQL')
    SQLALCHEMY_ECHO = environ.get('SQLALCHEMY_ECHO')

    UPLOAD_FOLDER = environ.get("UPLOAD_FOLDER")

