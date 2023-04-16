import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_instance_template_from_json
from utils.shared import check_gcp_params_from_request
from loguru import logger
from utils.exceptions import InvalidJsonException, UnAuthorizedException, InternalException  
from flask_restx import Resource, Api, Namespace, fields
from api.internal.cache import add_job
from api.internal.threads import AsyncOperationThread
from shared.core.kms_operations import key_ring_create, key_create
from api.internal.utils import admin_required

api = Namespace('kms', description='Key Management Service operations')



gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')




auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")

# key ring model 
key_ring_model = api.model('KeyRing', {
    'name': fields.String(required=True, description='Name of the Key Ring'),
    'location': fields.String(required=True, description='Location of the Key Ring'),
    })

# key model 
key_model = api.model('Key', {
    'name': fields.String(required=True, description='Name of the Key'),
    'location': fields.String(required=True, description='Location of the Key'),
    'key_ring': fields.String(required=True, description='Key Ring of the Key'),
})



@api.route('/keyRing')
class KeyRingList(Resource):
    @api.doc('Create Key Ring', description="API route to create a Key Ring, it launches key ring creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, key_ring_model, validate=True)
    @api.response(201, 'Key Ring created')
    @api.response(400, 'Error missing parameters')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the key ring')
    @admin_required
    def post(self):
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(e)
            return jsonify({'message': e.message}), 500
        except Exception as e:
            logger.error(e)
            return jsonify({'message': e.message}), 500

        # parse the json object
        try:
            key_ring  = key_ring_model.parse_args()

            job_id = str(uuid.uuid4()) 
            thread = AsyncOperationThread(job_id, gcp_project, operation=key_ring_create, key_ring_params=key_ring)
            thread.start()
            add_job(job_id, key_ring['name'], 'Key Ring Creation', 'PENDING')
            return {
                'name': job_id,
                'Key Ring Name': key_ring['name'],
                'type': 'Key Ring Creation',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(e)
            return jsonify({'message': 'Error parsing the json object'}), 400


@api.route('/keyRing/AsymetricKey')
class AsymetricKeyList(Resource):
    @api.doc('Create Asymetric Key', description="API route to create an Asymetric Key, it launches Asymetric Key creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, key_model, validate=True)
    @api.response(201, 'Asymetric Key created')
    @api.response(400, 'Error missing parameters')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the Asymetric Key')
    @admin_required
    def post(self):
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(e)
            return jsonify({'message': e.message}), 500
        except Exception as e:
            logger.error(e)
            return jsonify({'message': e.message}), 500

        # parse the json object
        try:
            key_params  = key_model.parse_args()
            job_id = str(uuid.uuid4()) 
            thread = AsyncOperationThread(job_id, gcp_project, operation=key_create, key_params=key_params)
            thread.start()
            add_job(job_id, key_params['name'], 'Asymetric Key Creation', 'PENDING')
            return {
                'name': job_id,
                'Key Name': key_params['name'],
                'type': 'Asymetric Key Creation',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(f"Error creating the key: {e}") 
            return {'error': "Error creating the key"}, 500






