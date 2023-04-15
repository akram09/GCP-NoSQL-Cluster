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
from shared.core.managed_instance_group_operations import create_managed_instance_group, update_managed_instance_group, delete_managed_instance_group
from api.internal.utils import admin_required



api = Namespace('managedInstanceGroup', description='Managed Instance Group operations')


gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')

region_parser = api.parser()
region_parser.add_argument('region', location='args', required=True, help='GCP region', default='us-central1')

auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")


# model for the manegedInstanceGroup
managed_instance_group_model = api.model('ManagedInstanceGroup', {
    'name': fields.String(required=True, description='Name of the Managed Instance Group'),
    'region': fields.String(required=True, description='Region of the Managed Instance Group'),
    'instance_template': fields.String(required=True, description='Instance Template of the Managed Instance Group'),
})




@api.route('/')
class managedInstanceGroupList(Resource):
    @api.doc('Create Managed Instance Group', description="API route to create a Managed Instance Group, it receives the parameters in JSON format and launch the managed instance group creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(managed_instance_group_model, gcp_parser, auth_token_parser, validate=True)
    @api.response(201, 'Managed Instance Group created')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the managed instance group')
    @admin_required
    def post(self):
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(f"Error checking gcp params: {e}")
            return {
                "error": e.message
            }, 401
        # receive json data from the request
        data = request.get_json()
        logger.info("Parsing parameters ...")
        try:
            if not data:
                raise InvalidJsonException()
            if not data.get('name'):
                raise InvalidJsonException()
            if not data.get('region'):
                raise InvalidJsonException()
            if not data.get('instance_template'):
                raise InvalidJsonException()
            managed_instance_group_params = {
                    'name': data.get('name'),
                    'region': data.get('region'),
                    'instance_template': data.get('instance_template')
                    }
            logger.info(f"Parameters parsed, managed instance group is {managed_instance_group_params}")
            
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=create_managed_instance_group, managed_instance_group_params=managed_instance_group_params)
            thread.start()
            add_job(job_id, managed_instance_group_params['name'], 'Managed Instance Group Creation', 'PENDING')
            return {
                'name': job_id,
                'Managed Instance Group Name': managed_instance_group_params['name'],
                'type': 'Managed Instance Group Creation',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error creating the managed instance group: {e}")
            return {'error': "Error creating the managed instance group"}, 500


@api.route('/<string:managed_instance_group_name>')
class ManagedInstanceGroup(Resource):
    @api.doc('Update Managed Instance Group', description="API route to update a Managed Instance Group, it receives the parameters in JSON format and launch the managed instance group update operation in the background. The route returns a job to check the status of the operation")
    @api.expect(managed_instance_group_model, gcp_parser, auth_token_parser, validate=True)
    @api.response(201, 'Managed Instance Group updated')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error updating the managed instance group')
    @admin_required
    def put(self, managed_instance_group_name):
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(f"Error checking gcp params: {e}")
            return {
                "error": e.message
            }, 401
        # receive json data from the request
        data = request.get_json()
        logger.info("Parsing parameters ...")
        try:
            if not data:
                raise InvalidJsonException()
            if not data.get('name'):
                raise InvalidJsonException()
            if not data.get('region'):
                raise InvalidJsonException()
            if not data.get('instance_template'):
                raise InvalidJsonException()
            managed_instance_group_params = {
                    'name': data.get('name'),
                    'region': data.get('region'),
                    'instance_template': data.get('instance_template')
            }
            logger.info(f"Parameters parsed, managed instance group is {managed_instance_group_params}")
            
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=update_managed_instance_group, managed_instance_group_params=managed_instance_group_params)
            thread.start()
            add_job(job_id, managed_instance_group_params['name'], 'Managed Instance Group Update', 'PENDING')
            return {
                'name': job_id,
                'Managed Instance Group Name': managed_instance_group_params['name'],
                'type': 'Managed Instance Group Update',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error updating the managed instance group: {e}")
            return {'error': "Error updating the managed instance group"}, 500
    
    @api.doc('Delete Managed Instance Group', description="API route to delete a Managed Instance Group, it receives the parameters in JSON format and launch the managed instance group deletion operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, region_parser, validate=True)
    @api.response(201, 'Managed Instance Group deleted')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error deleting the managed instance group')
    @admin_required
    def delete(self, managed_instance_group_name):
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(f"Error checking gcp params: {e}")
            return {
                "error": e.message
            }, 401

        logger.info("Parsing parameters ...")
        try:
            if not region_parser.parse_args().get('region'):
                raise InvalidJsonException()
            managed_instance_group_params = {
                    'name': managed_instance_group_name,
                    'region': region_parser.parse_args().get('region'),
            }
            logger.info(f"Parameters parsed, managed instance group is {managed_instance_group_params}")
            
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=delete_managed_instance_group, managed_instance_group_params=managed_instance_group_params)
            thread.start()
            add_job(job_id, managed_instance_group_params['name'], 'Managed Instance Group Deletion', 'PENDING')
            return {
                'name': job_id,
                'Managed Instance Group Name': managed_instance_group_params['name'],
                'type': 'Managed Instance Group Deletion',
                'status': 'PENDING'
            }, 201
