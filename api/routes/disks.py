# Description: Disks routes for the API
import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from loguru import logger
from utils.shared import check_gcp_params_from_request
from utils.exceptions import InvalidJsonException, UnAuthorizedException, InternalException
from flask_restx import Resource, Api, Namespace, fields
from api.internal.jobs_controller import check_job, get_job, update_job_status, get_job_list, add_job
from api.internal.utils import admin_required
from api.routes.cluster import gcp_parser, auth_token_parser
from shared.core.attach_disk import attach_disk_to_instance
from api.internal.threads import AsyncOperationThread

# create job namespace 
api = Namespace('disks', description='Disks operations')


# create attached disk to instance model 
attached_disk_model = api.model('AttachedDiskToInstance', {
    'zone': fields.String(required=True, description='The zone of the instance'),
    'type': fields.String(required=True, description='The type of the disk'),
    'size': fields.Integer(required=True, description='The size of the disk'),
    'image_family': fields.String(required=False, description='The image family to use'),
    'image_project': fields.String(required=False, description='The image project to use'),
    'auto_delete': fields.Boolean(required=False, description='Whether the disk should be deleted when the instance is deleted'),
    'instance_name': fields.String(required=True, description='The name of the instance to attach the disk to'),
    'disk_name': fields.String(required=True, description='The name of the disk to attach to the instance')
    })



gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')


auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")


@api.route('/attach')
class AttachDiskToInstance(Resource):
    @api.doc('attach_disk_to_instance')
    @api.expect(attached_disk_model, gcp_parser, auth_token_parser, validate=True)
    @api.response(200, 'Disk attached successfully')
    @api.response(400, 'Invalid request')
    @api.response(401, 'Unauthorized')
    @admin_required
    def post(self):
        """
        Attach a disk to an instance
        """
        gcp_args = gcp_parser.parse_args()
        gcp_project = None
        # check gcp params
        try:
            gcp_project = check_gcp_params_from_request(gcp_args)
        except InternalException as e:
            logger.error(e)
            return {'error': e.message}, 500
        except Exception as e:
            logger.error(e)
            return {'error': e.message}, 500
        
        # parse request body 
        try:
            attach_disk_instance = request.get_json()
            if not attach_disk_instance:
                raise InvalidJsonException('Invalid json object')

            job_id = str(uuid.uuid4()) 
            thread = AsyncOperationThread(job_id, gcp_project, operation=attach_disk_to_instance,
                zone = attach_disk_instance['zone'],
                disk_name = attach_disk_instance['disk_name'],
                instance_name = attach_disk_instance['instance_name'],
                disk_type = attach_disk_instance['type'],
                disk_size_gb = attach_disk_instance['size'],
                image_family = attach_disk_instance['image_family'],
                image_project = attach_disk_instance['image_project'],
                auto_delete = attach_disk_instance['auto_delete']
            )
            thread.start()
            add_job(job_id, attach_disk_instance["instance_name"], 'Attach Disk to Instance', 'PENDING', gcp_project.project_id)
            return {
                'name': job_id,
                'instance-name': attach_disk_instance['instance_name'],
                'type': 'Attach Disk to Instance',
                'project-id': gcp_project.project_id, 
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(e)
            return {'error': "Error attaching disk"}, 500

