# Description: API routes to create and delete GCP Storage Buckets
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
from shared.core.storage_operations import create_gcp_bucket, delete_gcp_bucket 
from api.internal.utils import admin_required


api = Namespace('storage', description='GCP Storage operations')

gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')


auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")


# bucket model 
bucket_model = api.model('Bucket', {
    'name': fields.String(required=True, description='Name of the Bucket'),
    'location': fields.String(required=True, description='Location of the Bucket'),
    'key_name': fields.String(required=True, description='Key name to encrypt the bucket (Full name of the key, e.g. projects/upwork-project-gcp/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key', default="projects/upwork-project-gcp/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key")
    })




@api.route('/bucket')
class BucketList(Resource):
    @api.doc('Create Bucket', description="API route to create a Bucket, it launches bucket creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, bucket_model, validate=True)
    @api.response(201, 'Bucket created')
    @api.response(400, 'Error missing parameters')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the bucket')
    @admin_required
    def post(self):
        """
        API route to create a Bucket, it launches bucket creation operation in the background. The route returns a job to check the status of the operation
        """
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InvalidJsonException as e:
            logger.error(e)
            return {'message': 'Invalid json'}, 400
        except Exception as e:
            logger.error(e)
            return {'message': 'Internal error'}, 500
        # parse bucket params
        # launch bucket creation operation in the background
        try:
            bucket_params = request.get_json()
            job_id = str(uuid.uuid4()) 
            add_job(job_id, bucket_params['name'], 'GCP Storage Bucket Creation', 'PENDING')
            thread = AsyncOperationThread(job_id, gcp_project, operation=create_gcp_bucket, bucket_params=bucket_params)
            thread.start()
            return {
                'name': job_id,
                'Bucket Name': bucket_params['name'],
                'type': 'GCP Storage Bucket Creation',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(e)
            return {'message': 'Internal error'}, 500


@api.route('/bucket/<string:bucket_name>')
class Bucket(Resource):
    @api.doc('Delete Bucket', description="API route to delete a Bucket, it launches bucket deletion operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, validate=True)
    @api.response(202, 'Bucket deletion started')
    @api.response(400, 'Error missing parameters')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error deleting the bucket')
    @admin_required
    def delete(self, bucket_name):
        """
        API route to delete a Bucket, it launches bucket deletion operation in the background. The route returns a job to check the status of the operation
        """
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InvalidJsonException as e:
            logger.error(e)
            return {'message': 'Invalid json'}, 400
        except Exception as e:
            logger.error(e)
            return {'message': 'Internal error'}, 500
        # launch bucket deletion operation in the background
        try:
            bucket_params = {'name': bucket_name}
            job_id = str(uuid.uuid4()) 
            add_job(job_id, bucket_name, 'GCP Storage Bucket Delete', 'PENDING')
            thread = AsyncOperationThread(job_id, gcp_project, operation=delete_gcp_bucket, bucket_params=bucket_params)
            thread.start()
            return {
                'name': job_id,
                'Bucket Name': bucket_name,
                'type': 'GCP Storage Bucket Delete',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(e)
            return {'message': 'Internal error'}, 500
