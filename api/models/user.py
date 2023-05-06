# Purpose: User Model
# Description: This file contains the User model. The User model is used to store user information in the database.
from api.extensions import db, bcrypt
from flask import current_app as app
import datetime
from loguru import logger
import jwt

class User(db.Model):
    # auto generate id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.role = role

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def encode_auth_token(self, user_id, role):
        """
        Generates the Auth Token
        :return: string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, minutes=60),
            'iat': datetime.datetime.utcnow(),
            'sub': {
                'id': str(user_id),
                'role': role
            }
        }
        token =  jwt.encode(
            payload,
            app.config.get('SECRET_KEY')[0],
            algorithm='HS256'
        )
        return token

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY')[0], algorithms='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            logger.error('Signature expired. Please log in again.')
            return None
        except jwt.InvalidTokenError as e :
            logger.error('Invalid token. Please log in again.')
            return None
