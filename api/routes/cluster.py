"""
This module contains the API routes to create, update and delete clusters.
"""
import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from utils.shared import check_gcp_params_from_request
from loguru import logger
from utils.exceptions import InvalidJsonException, UnAuthorizedException, InternalException  
from shared.core.create_cluster import create_cluster
from shared.core.update_cluster import update_cluster
from shared.entities.cluster import ClusterUpdateType
from flask_restx import Resource, Api, Namespace, fields
from api.internal.cache import add_job
from api.internal.threads import CreateClusterThread, UpdateClusterThread, MigrateClusterThread
from api.internal.utils import admin_required



# create cluster namespace 
api = Namespace('clusters', description='Cluster operations')

# create the storage model 
storage_model = api.model('Storage', {
    'type': fields.String(required=False, description='The type of the storage'),
    'bucket': fields.String(required=True, description='The bucket name to use'),
})


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
template_model = api.model('ClusterTemplate', {
    'name': fields.String(required=False, description='The name of the template'),
    'machine_type': fields.String(required=False, description='The machine type to use'),
    'image_family': fields.String(required=False, description='The image family to use'),
    'image_project': fields.String(required=False, description='The image project to use'),
    'disks': fields.List(fields.Nested(disk_model), required=False, description='The disks to use'),
    'labels': fields.List(fields.Nested(labels_model), required=False, description="Instance Template labels")
})

couchbase_creds_model = api.model('CouchbaseCreds', {
    'username': fields.String(required=True, description='The username to use'),
    'password': fields.String(required=True, description='The password to use'),
})

# create cluster model
cluster_model = api.model('Cluster', {
    'name': fields.String(read_only=True, required=True, description='The name of the cluster'),
    'size': fields.Integer(required=True, description='The size of the cluster'), 
    'region': fields.String(required=True, description='The region of the cluster'),
    'storage': fields.Nested(storage_model, required=True, description='The storage definition'),
    'template': fields.Nested(template_model, required=False, description='The template definition'),
    'couchbase': fields.Nested(couchbase_creds_model, required=False, description='The couchbase credentials'),
})




gcp_parser = api.parser()
# gcp project id 
gcp_parser.add_argument('project-id', location='args', required=True, help='GCP project id', default='upwork-project-gcp')
# gcp project number
gcp_parser.add_argument('project-number', location='args', required=True, help='GCP project number', default='1546856')


auth_token_parser =api.parser()
auth_token_parser.add_argument('Authorization', location='headers', required=True, help="Authentication token to access the api routes")


# cluster update query parameters parser 
cluster_update_parser = api.parser()
cluster_update_parser.add_argument('migrate', location='args', type=int, help='Whether to migrate the cluster (0/1)', default=0)



# create a cluster list resource
@api.route('/')
class ClusterList(Resource):
    @api.doc('create_cluster', description="API route to create a cluster, it receives the cluster parameters in JSON format and launch the cluster creation operation in the background. The route returns a job to check the status of the operation")
    @api.expect(gcp_parser, cluster_model, auth_token_parser, validate=True)
    @api.response(201, 'Cluster created')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error creating the cluster')
    @admin_required
    def post(self):
        """
        API route to create a cluster, it receives the cluster parameters in JSON format and launch the cluster creation operation in the background. The route returns a job to check the status of the operation.
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
            cluster = parse_cluster_def_from_json(data)
            logger.info(f"Parameters parsed, cluster is {cluster}")

            # create cluster
            job_id = str(uuid.uuid4())
            thread = CreateClusterThread(job_id, gcp_project, cluster, data)
            thread.start()
            add_job(job_id, cluster.name, 'Cluster Creation', 'PENDING')
            return {
                'name': job_id,
                'cluster_name': cluster.name,
                'type': 'Cluster Creation',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error creating the cluster: {e}")
            return {'error': "Error creating the cluster"}, 500


# update a cluster resource
@api.route('/<string:cluster_name>')
class Cluster(Resource):

    @api.doc('update_cluster', description="API route to update a cluster, it receives the cluster parameters in JSON format and launch the cluster update operation in the background. The route returns a job to check the status of the operation, NOTE: The cluster update can either be in the rolling mode or no migration mode depending on the parameter `migrate`") 
    @api.expect(cluster_model, gcp_parser, cluster_update_parser,auth_token_parser,validate=True)
    @api.response(201, 'Cluster updated')
    @api.response(400, 'Error parsing the json object')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error updating the cluster')
    @admin_required
    def put(self, cluster_name):
        """
        API route to update a cluster, it receives the cluster parameters in JSON format and launch the cluster update operation in the background. The route returns a job to check the status of the operation, NOTE: The cluster update can either be in the rolling mode or no migration mode depending on the parameter `migrate`
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
            cluster = parse_cluster_def_from_json(data)
            migrate = cluster_update_parser.parse_args()['migrate']
            cluster_update_type = ClusterUpdateType.UPDATE_AND_MIGRATE if migrate else ClusterUpdateType.UPDATE_NO_MIGRATE
            logger.info(f"Parameters parsed, cluster is {cluster}")

            # update cluster
            job_id = str(uuid.uuid4())
            thread = UpdateClusterThread(job_id, gcp_project, cluster, cluster_update_type)
            thread.start()
            add_job(job_id, cluster.name, 'Cluster Update', 'PENDING')
            return {
                'name': job_id,
                'cluster_name': cluster.name,
                'type': 'Cluster Update',
                'status': 'PENDING'
            }, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error updating the cluster: {e}")
            return {'error': "Error updating the cluster"}, 500




cluster_migration_parser = api.parser()
cluster_migration_parser.add_argument('cluster_region', location='args', required=True, type=str, help='Cluster region to migrate', default='us-central1')

# migrate cluster to the last update
@api.route('/<string:cluster_name>/migrate')
class Cluster(Resource):

    @api.doc('migrate_cluster', description="API route to migrate the cluster to the last update created. It returns a job to check the status of the operation") 
    @api.expect(gcp_parser, cluster_update_parser, auth_token_parser, validate=True)
    @api.response(201, 'Cluster migrated')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error updating the cluster')
    @admin_required
    def post(self, cluster_name):
        """
        API route to migrate the cluster to the last update created. It returns a job to check the status of the operation
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

        try:
            cluster_region = cluster_migration_parser.parse_args()['cluster_region']
            # update cluster
            job_id = str(uuid.uuid4())
            thread = MigrateClusterThread(job_id, gcp_project, cluster_name, cluster_region)
            thread.start()
            add_job(job_id, cluster_name, 'Cluster Migrate', 'PENDING')
            return {
                'name': job_id,
                'cluster_name': cluster_name,
                'type': 'Cluster Migrate',
                'status': 'PENDING'
            }, 201
        except Exception as e:
            logger.error(f"Error updating the cluster: {e}")
            return {'error': "Error updating the cluster"}, 500
