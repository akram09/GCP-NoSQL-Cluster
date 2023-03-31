import os
import base64
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = base64.b64encode(os.urandom(24)).decode('utf-8'),
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_TRACK_MODIFICATIONS = False

