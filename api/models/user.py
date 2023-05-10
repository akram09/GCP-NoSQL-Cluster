# Purpose: User Model
# Description: This file contains the User model. The User model is used to store user information in the database.
from api.extensions import bcrypt
from flask import current_app as app
import datetime
from loguru import logger
import jwt
import uuid

class User():
    def __init__(self, username, password, role="user", id=None):
        # generate id 
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())  
        self.username = username
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "registered_on": self.registered_on.isoformat(),
            "role": self.role
        }
    
    @staticmethod
    def from_dict(user_dict):
        return User(
            user_dict["username"],
            user_dict["password"],
            user_dict["role"],
            user_dict["id"]
        )

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
