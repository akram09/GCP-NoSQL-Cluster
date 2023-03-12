import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from utils.json import parse_cluster_def_from_json
from loguru import logger
from utils.exceptions import JsonParseException
from utils.create_cluster import create_cluster
from utils.update_cluster import update_cluster

bp = Blueprint('cluster', __name__, url_prefix='/api/cluster')



@bp.route('/<str:cluster_name>', methods=('POST'))
def create_gcp_cluster(cluster_name):
    if request.method == 'POST':
        # receive json data from the request
        data = request.get_json()
        # get the gcp project from the global g
        gcp_project = g.gcp_project

        logger.info("Parsing parameters ...")
        try:
            cluster = parse_cluster_def_from_json(data, cluster_name)
            logger.info(f"Parameters parsed, cluster is {cluster}")

            # create cluster
            create_cluster(gcp_project, cluster)
        except JsonParseException as e:
            logger.error(f"Error parsing the json object: {e}")
            return jsonify({'error': "Error parsing the json object"}), 400



        return 'Create GCP Cluster'

@bp.route('/<str:cluster_name>', methods=('PUT'))
def update_gcp_cluster(cluster_name):
    if request.method == 'PUT': 
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

        except JsonParseException as e:
            logger.error(f"Error parsing the json object: {e}")
            return jsonify({'error': "Error parsing the json object"}), 400



        return 'Create GCP Cluster'

