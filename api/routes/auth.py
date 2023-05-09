""""
Authentications related routes, such as login and register
"""
import functools
import os
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from loguru import logger
from utils.shared import check_gcp_params_from_request
from utils.exceptions import InvalidJsonException, UnAuthorizedException, UserWithUsernameAlreadyExistsException, UserAlreadyExistsException, UserDoesNotExistException, InvalidPasswordException
from utils.env import update_service_account_oauth_token
from flask_restx import Resource, Api, Namespace, fields
from api.models.user import User
from api.internal.utils import admin_required
from api.internal.auth_controller import register_user, login_user
# create auth namespace
api = Namespace('auth', description='Authentications related operations')


registration_request = api.model('RegistrationRequest', {
    'username': fields.String(required=True, description='The username of the user'),
    'password': fields.String(required=True, description='The password of the user'),
    'role': fields.String(required=True, description='The role of the user')
})
login_request = api.model('LoginRequest', {
    'username': fields.String(required=True, description='The username of the user'),
    'password': fields.String(required=True, description='The password of the user')
})

oauth_token_update_request = api.model('OAuthToken', {
    'token': fields.String(required=True, description="The Google Cloud Platform OAuth token")
})


@api.route('/register')
class AuthRegister(Resource):
    
    # register a new user route
    @api.doc('register a new user', description="API route to register a new user. The `username` parameter is the username of the user. The `password` parameter is the password of the user. The `role` parameter is the role of the user.")
    @api.expect(registration_request, validate=True)
    @api.response(200, 'User registered')
    @api.response(400, 'Bad request')
    @api.response(500, 'Error registering the user')
    def post(self):
        """
        Register a new user, the route expects a json body that contains user informations. 
        It returns a jwt token that can be used to authenticate the user in the future.
        """
        # get the json data
        data = request.get_json()
        # check if the json data is valid
        if not data:
            raise InvalidJsonException()
        # create a new user
        user = User(
            data['username'],
            data['password'],
            data['role']
        )
        try: 
            token = register_user(user)
            return {
                "message": "User registered",
                "token": token
            }, 200
        except UserAlreadyExistsException as e:
            logger.error(e)
            return {
                "message": "User already exists"
            }, 400
        except Exception as e:
            logger.error(e)
            return {
                "message": "Error registering the user"
            }, 500

# login route
@api.route('/login')
class AuthLogin(Resource):
    @api.doc('login a user', description="API route to login a user. The `username` parameter is the username of the user. The `password` parameter is the password of the user.")
    @api.expect(login_request, validate=True)
    @api.response(200, 'User logged in')
    @api.response(400, 'Bad request')
    @api.response(500, 'Error logging in the user')
    def post(self):
        """
        Login a user, the route expects a json body that contains user informations. 
        It returns a jwt token that can be used to authenticate the user in the future.
        """
        # get the json data
        data = request.get_json()
        # check if the json data is valid
        if not data:
            raise InvalidJsonException()
        try:
            token = login_user(data['username'], data['password'])
        except UserDoesNotExistException as e:
            logger.error(e)
            return {
                "message": "User does not exist"
            }, 400
        except InvalidPasswordException as e:
            logger.error(e)
            return {
                "message": "Incorrect password"
            }, 400
        except Exception as e:
            logger.error(e)
            return {
                "message": "Error logging in the user"
            }, 500
        # generate jwt token
        return {
            "message": "User logged in",
            "token": token
        }, 200


# oauth tokens
@api.route('/oauth/tokens', doc=False)
class OauthTokens(Resource):
    @api.doc('Update OAuth token', description="API route to update the Google Cloud Platform OAuth token that is used by this server to authenticate all the requests")
    @api.expect(oauth_token_update_request, validate=True)
    @api.response(200, 'Token Updated')
    @api.response(400, 'Bad request')
    @admin_required
    def post(self):
        """
        Update the Google Cloud Platform OAuth token that is used by this server to authenticate all the requests
        """

        # get the json data
        data = request.get_json()
        # check if the json data is valid
        if not data:
            raise InvalidJsonException()
        # get the token 
        token = data["token"]

        update_service_account_oauth_token(token)

        return {
            "message": "OAuth token updated successfully",
        }, 200
