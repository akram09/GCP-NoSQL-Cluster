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
from api.internal.cache import check_job, get_job, update_job_status, get_job_list
from api.routes.cluster import header_parser

# create job namespace 
api = Namespace('jobs', description='Job operations')


# create the job model 
job_model = api.model('Job', {
    'name': fields.String(required=True, description='The name of the job'),
    'cluster_name': fields.String(required=True, description='The cluster to use'),
    'type': fields.String(required=True, description='The type of the job'),
    'status': fields.String(required=True, description='The status of the job'),
})





job_list_parser = api.parser() 
job_list_parser.add_argument('status', type=str, help='The status of the job', location='args')
job_list_parser.add_argument('type', type=str, help='The type of the job', location='args')
job_list_parser.add_argument('cluster_name', type=str, help='The cluster name of the job', location='args')
# job list resource 
@api.route('/')
class JobList(Resource):
    
    # get job list route
    @api.doc('get_job_list', description="API route to get the list of jobs and their status. The `status` parameter can be used to filter the jobs by status. The `type` parameter can be used to filter the jobs by type. The `cluster_name` parameter can be used to filter the jobs by cluster name.")
    @api.expect(job_list_parser, header_parser, validate=True)
    @api.response(200, 'Job list found')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error getting the job list')
    def get(self):

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

        jobs_list = get_job_list()
        args = job_list_parser.parse_args()
        status = args.get('status')
        type = args.get('type')
        cluster_name = args.get('cluster_name')
        # filter list by status
        if status:
            jobs_list = list(filter(lambda job: job['status'] == status, jobs_list))
        # filter list by type
        if type:
            jobs_list = list(filter(lambda job: job['type'] == type, jobs_list))
        # filter list by cluster name
        if cluster_name:
            jobs_list = list(filter(lambda job: job['cluster_name'] == cluster_name, jobs_list))
        return jobs_list, 200


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

