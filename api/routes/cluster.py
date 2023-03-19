import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from loguru import logger
from utils.exceptions import InvalidJsonException
from shared.core.create_cluster import create_cluster
from shared.core.update_cluster import update_cluster
from flask_restx import Resource, Api, Namespace, fields
from api.internal.cache import add_job
from api.internal.threads import CreateClusterThread, UpdateClusterThread


# create cluster namespace 
api = Namespace('cluster', description='Cluster operations')

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

template_model = api.model('Template', {
    'name': fields.String(required=False, description='The name of the template'),
    'machine_type': fields.String(required=False, description='The machine type to use'),
    'image_family': fields.String(required=False, description='The image family to use'),
    'image_project': fields.String(required=False, description='The image project to use'),
    'disks': fields.List(fields.Nested(disk_model), required=False, description='The disks to use'),
})

# create cluster model
cluster_model = api.model('Cluster', {
    'name': fields.String(read_only=True, required=True, description='The name of the cluster'),
    'size': fields.Integer(required=True, description='The size of the cluster'), 
    'region': fields.String(required=True, description='The region of the cluster'),
    'storage': fields.Nested(storage_model, required=True, description='The storage definition'),
    'template': fields.Nested(template_model, required=False, description='The template definition'),
})


# create a cluster list resource
@api.route('/')
class ClusterList(Resource):
    @api.doc('create_cluster')
    @api.expect(cluster_model)
    @api.response(201, 'Cluster created')
    @api.response(400, 'Error parsing the json object')
    @api.response(500, 'Error creating the cluster')
    def post(self):
        # receive json data from the request
        data = request.get_json()
        # get the gcp project from the global g
        gcp_project = g.gcp_project

        logger.info("Parsing parameters ...")
        try:
            cluster = parse_cluster_def_from_json(data)
            logger.info(f"Parameters parsed, cluster is {cluster}")

            # create cluster
            job_id = str(uuid.uuid4())
            thread = CreateClusterThread(job_id, gcp_project, cluster)
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


# create a cluster resource
@api.route('/<string:cluster_name>')
class Cluster(Resource):

    @api.doc('update_cluster')
    @api.expect(cluster_model)
    @api.response(201, 'Cluster updated')
    @api.response(400, 'Error parsing the json object')
    @api.response(500, 'Error updating the cluster')
    def put(self, cluster_name):
        # receive json data from the request
        data = request.get_json()
        # get the gcp project from the global g
        gcp_project = g.gcp_project

        logger.info("Parsing parameters ...")
        try:
            cluster = parse_cluster_def_from_json(data, cluster_name)
            logger.info(f"Parameters parsed, cluster is {cluster}")

            # update cluster
            update_cluster(gcp_project, cluster)
            return api.payload, 201
        except InvalidJsonException as e:
            logger.error(f"Error parsing the json object: {e}")
            return {'error': "Error parsing the json object"}, 400
        except Exception as e:
            logger.error(f"Error updating the cluster: {e}")
            return {'error': "Error updating the cluster"}, 500



