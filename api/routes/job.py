import functools
import uuid
import threading
from flask import (
  flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.parse_requests import parse_cluster_def_from_json
from loguru import logger
from utils.exceptions import InvalidJsonException
from flask_restx import Resource, Api, Namespace, fields

# create job namespace 
api = Namespace('job', description='Job operations')


# create the job model 
job_model = api.model('Job', {
    'name': fields.String(required=True, description='The name of the job'),
    'cluster_name': fields.String(required=True, description='The cluster to use'),
    'type': fields.String(required=True, description='The type of the job'),
    'status': fields.String(required=True, description='The status of the job'),
})



# create a cluster resource
@api.route('/<string:job_id>')
class Job(Resource):

    # get job route, check in the current threads 
    @api.doc('get_job')
    @api.response(200, 'Job found')
    @api.response(404, 'Job not found')
    @api.response(500, 'Error getting the job')
    def get(self, job_id):
        # check if a thread with the given id exists
        if job_id in threading.enumerate():
            # return the thread status 
            return {'status': threading.enumerate()[job_id].status,
                    'name': threading.enumerate()[job_id].name,
            }, 200
        



    @api.doc('get_job')
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



