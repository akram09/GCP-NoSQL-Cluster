# Description: API routes to manage Instance Templates
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
from shared.core.instance_template_operations import create_instance_template, update_instance_template, delete_instance_template
from api.internal.utils import admin_required



api = Namespace('instanceTemplates', description='Instance Templates operations')


gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')


auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")


# create the disk model 
disk_model = api.model('Disk', {
    'type': fields.String(required=True, description='The type of the disk'),
    'size': fields.Integer(required=True, description='The size of the disk'),
    'boot': fields.Boolean(required=True, description='Whether the disk is a boot disk'),
})

labels_model = api.model('Label', {
    "key": fields.String(required=True, description="Label key", default="key"),
    "value": fields.String(required=True, description="Label value", default="value"),
})
template_model = api.model('InstanceTemplate', {
    'name': fields.String(required=False, description='The name of the template'),
    'region': fields.String(required=False, description='The region to use'),
    'machine_type': fields.String(required=False, description='The machine type to use'),
    'image_family': fields.String(required=False, description='The image family to use'),
    'image_project': fields.String(required=False, description='The image project to use'),
    'disks': fields.List(fields.Nested(disk_model), required=False, description='The disks to use'),
    'labels': fields.List(fields.Nested(labels_model), required=False, description="Instance Template labels"),
    'startup_script_url': fields.String(required=False, description='The instance template startup script url'),
    'shutdown_script_url': fields.String(required=False, description='The instance template shutdown script url')
})




@api.route('/')
class InstanceTemplateList(Resource):
    @api.doc('Create Instance Template', description="API route to create an Instance Template, it receives the parameters in JSON format and launch the instance template creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, template_model, auth_token_parser, validate=True)
    @api.response(201, 'Instance Template created')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the instance template')
    @admin_required
    def post(self):
        """
        API route to create an Instance Template, it receives the parameters in JSON format and launch the instance template creation operation in the background. The route returns a job to check the status of the operation
        """
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
            template = parse_instance_template_from_json(data)
            logger.info(f"Parameters parsed, template is {template}")
            
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=create_instance_template, instance_template_params=template)
            thread.start()
            add_job(job_id, template.name, 'Instance Template Creation', 'PENDING')
            return {
                'name': job_id,
                'instance_template_name': template.name,
                'type': 'Instance Template Creation',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error creating the instance template: {e}")
            return {'error': "Error creating the instance template"}, 500


@api.route('/<string:template_name>')
class InstanceTemplate(Resource):
    @api.doc('Update Instance Template', description="API route to update an Instance Template, it receives the parameters in JSON format and launch the instance template update operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, template_model, auth_token_parser, validate=True)
    @api.response(201, 'Instance Template updated')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error updating the instance template')
    @admin_required
    def put(self, template_name):
        """
        API route to update an Instance Template, it receives the parameters in JSON format and launch the instance template update operation in the background. The route returns a job to check the status of the operation
        """
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
            template = parse_instance_template_from_json(data)
            logger.info(f"Parameters parsed, template is {template}")
            
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=update_instance_template, instance_template_params=template)
            thread.start()
            add_job(job_id, template.name, 'Instance Template Update', 'PENDING')
            return {
                'name': job_id,
                'instance_template_name': template.name,
                'type': 'Instance Template Update',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error updating the instance template: {e}")
            return {'error': "Error updating the instance template"}, 500

    @api.doc('Delete Instance Template', description="API route to delete an Instance Template, it receives the parameters in JSON format and launch the instance template deletion operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, auth_token_parser, validate=True)
    @api.response(201, 'Instance Template deleted')
    @api.response(500, 'Error deleting the instance template')
    @admin_required
    def delete(self, template_name):
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
        try:
            # run the async operation
            job_id = str(uuid.uuid4())
            thread = AsyncOperationThread(job_id, gcp_project, operation=delete_instance_template, instance_template_name=template_name)
            thread.start()
            add_job(job_id, template_name, 'Instance Template Deletion', 'PENDING')
            return {
                'name': job_id,
                'instance_template_name': template_name,
                'type': 'Instance Template Deletion',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(f"Error deleting the instance template: {e}")
            return {'error': "Error deleting the instance template"}, 500

