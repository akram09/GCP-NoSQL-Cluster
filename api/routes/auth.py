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
from utils.exceptions import InvalidJsonException, UnAuthorizedException, UserWithUsernameAlreadyExistsException
from utils.env import update_service_account_oauth_token
from flask_restx import Resource, Api, Namespace, fields
from api.extensions import db
from api.models.user import User
from sqlalchemy.exc import IntegrityError
from api.internal.utils import admin_required
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
        # get the json data
        data = request.get_json()
        # check if the json data is valid
        if not data:
            raise InvalidJsonException()
        # create a new user
        user = User(
            username=data['username'],
            password=data['password'],
            role=data['role']
        )
        # add the user to the database
        db.session.add(user)
        try: 
            db.session.commit()
            # generate jwt token 
            token = user.encode_auth_token(user.id, user.role)
            return {
                "message": "User registered",
                "token": token
            }, 200
        # catch integrity error
        except IntegrityError:
            return {
                "message": "User with username already exists"
            }, 400
        except Exception as e:
            raise e
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
        # get the json data
        data = request.get_json()
        # check if the json data is valid
        if not data:
            raise InvalidJsonException()
        # get the user
        user = User.query.filter_by(username=data['username']).first()
        # check if the user exists
        if not user:
            return {
                "message": "User does not exist"
            }, 400
        # check if the password is correct
        if not user.check_password(data['password']):
            return {
                "message": "Incorrect password"
            }, 400
        # generate jwt token
        token = user.encode_auth_token(user.id, user.role)
        return {
            "message": "User logged in",
            "token": token
        }, 200


# oauth tokens
@api.route('/oauth/tokens')
class OauthTokens(Resource):
    # @api.doc('Update OAuth token', description="API route to update the Google Cloud Platform OAuth token that is used by this server to authenticate all the requests")
    @api.expect(oauth_token_update_request, validate=True)
    @api.response(200, 'Token Updated')
    @api.response(400, 'Bad request')
    @admin_required
    def post(self):
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
