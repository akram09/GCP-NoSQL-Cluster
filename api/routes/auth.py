import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from loguru import logger
from utils.shared import check_gcp_params_from_request
from utils.exceptions import InvalidJsonException, UnAuthorizedException
from flask_restx import Resource, Api, Namespace, fields
from api.extensions import db
# create auth namespace
api = Namespace('auth', description='Authentications related operations')


# create the auth user 
auth_user = api.model('AuthUser', {
    'username': fields.String(required=True, description='The username of the user'),
    'password': fields.String(required=True, description='The password of the user')
    'role': fields.String(required=True, description='The role of the user')
})


@api.route('/register')
class AuthRegister(Resource):
    
    # register a new user route
    @api.doc('register a new user', description="API route to register a new user. The `username` parameter is the username of the user. The `password` parameter is the password of the user. The `role` parameter is the role of the user.")
    @api.expect(auth_user, validate=True)
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
        user = Users(
            username=data['username'],
            password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            role=data['role']
        )
        # add the user to the database
        db.session.add(user)
        db.session.commit()
        return {
            "message": "User registered"
        }, 200



@api.route('/<string:job_id>')
class Job(Resource):

    # get job route, check in the current threads 
    @api.doc('get_job')
    @api.expect(header_parser, validate=True)
    @api.response(200, 'Job found')
    @api.response(401, 'Unauthorized request')
    @api.response(404, 'Job not found')
    @api.response(500, 'Error getting the job')
    def get(self, job_id):

        # get headers
        headers = header_parser.parse_args()
        gcp_args = {
            'project_id': headers['GCPProject'],
            'oauth_token': headers['Authorization'],
            'project_number': headers['GCPProjectNumber']
        }
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except UnAuthorizedException as e:
            logger.error(f"Error checking gcp params: {e}")
            return {
                "error": e.message
            }, 401
        # check first if the job is in the jobs dictionary
        if check_job(job_id):
            get_job(job_id), 200
        else:
            return {'error': 'Job not found'}, 404

