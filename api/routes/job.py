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
from api.internal.cache import check_job, get_job, update_job_status

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
        threads = threading.enumerate()
        threads_names = [thread.name for thread in threads]
        # check first if the job is in the jobs dictionary
        if check_job(job_id):
            # check if a thread with the given id exists
            if job_id in threads_names:
                return get_job(job_id), 200
            else:
                if get_job(job_id)['status'] == 'FAILED':
                    return get_job(job_id), 200 
                # update the status of the job
                update_job_status(job_id, 'COMPLETED')
                # return the job
                return get_job(job_id), 200
        else:
            return {'error': 'Job not found'}, 404

