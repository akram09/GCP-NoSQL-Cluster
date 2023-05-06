# Description: Job routes for the API
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
from api.internal.jobs_controller import check_job, get_job, update_job_status, get_job_list
from api.internal.utils import admin_required
from api.routes.cluster import gcp_parser, auth_token_parser

# create job namespace 
api = Namespace('jobs', description='Job operations')


# create the job model 
job_model = api.model('Job', {
    'name': fields.String(required=True, description='The name of the job'),
    'cluster_name': fields.String(required=True, description='The cluster to use'),
    'type': fields.String(required=True, description='The type of the job'),
    'status': fields.String(required=True, description='The status of the job'),
    'project-id': fields.String(required=True, description='The project id of the job'),
})





job_list_parser = api.parser() 
job_list_parser.add_argument('status', type=str, help='The status of the job', location='args')
job_list_parser.add_argument('type', type=str, help='The type of the job', location='args')
job_list_parser.add_argument('cluster_name', type=str, help='The cluster name of the job', location='args')
job_list_parser.add_argument('project-id', type=str, help='The project id of the job', location='args')
# job list resource 
@api.route('/')
class JobList(Resource):
    
    # get job list route
    @api.doc('get_job_list', description="API route to get the list of jobs and their status. The `status` parameter can be used to filter the jobs by status. The `type` parameter can be used to filter the jobs by type. The `cluster_name` parameter can be used to filter the jobs by cluster name.")
    @api.expect(gcp_parser, job_list_parser, auth_token_parser, validate=True)
    @api.response(200, 'Job list found')
    @api.response(401, 'Unauthorized request')
    @api.response(500, 'Error getting the job list')
    @admin_required
    def get(self):
        """
        API route to get the list of jobs and their status. The `status` parameter can be used to filter the jobs by status. The `type` parameter can be used to filter the jobs by type. The `cluster_name` parameter can be used to filter the jobs by cluster name.
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

        jobs_list = get_job_list()
        args = job_list_parser.parse_args()
        status = args.get('status')
        job_type = args.get('type')
        cluster_name = args.get('cluster_name')
        project_id = args.get('project-id')
        # filter list by status
        if status:
            jobs_list = list(filter(lambda job: job['status'] == status, jobs_list))
        # filter list by type
        if job_type:
            jobs_list = list(filter(lambda job: job['type'] == job_type, jobs_list))
        # filter list by cluster name
        if cluster_name:
            jobs_list = list(filter(lambda job: job['cluster_name'] == cluster_name, jobs_list))
        # filter list by project 
        if project_id:
            jobs_list = list(filter(lambda job: job['project-id'] == project_id, jobs_list))
        return jobs_list, 200


@api.route('/<string:job_id>')
class Job(Resource):

    # get job route, check in the current threads 
    @api.doc('get_job')
    @api.expect(gcp_parser, auth_token_parser, validate=True)
    @api.response(200, 'Job found')
    @api.response(401, 'Unauthorized request')
    @api.response(404, 'Job not found')
    @api.response(500, 'Error getting the job')
    def get(self, job_id):
        """
        API route to get the status of a job. The `job_id` parameter is the id of the job to get the status.
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
        # check first if the job is in the jobs dictionary
        if check_job(job_id):
            get_job(job_id), 200
        else:
            return {'error': 'Job not found'}, 404

