""""
This module contains the create command for the cli. 
"""

from loguru import logger
from utils.shared import check_gcp_params
from utils.args import cluster_from_args
from shared.core.create_cluster import create_cluster



def create_cluster(args):
    """"
    Create a new cluster on the Google Cloud Platform.
    """
    logger.info("Welcome to the cluster creation script")
    logger.info("Checking parameters ...")
    # checking the parameters and loading the project
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")

    # parse parameters 
    logger.info("Parsing parameters ...")
    # parse the cluster parameters from the command line arguments
    cluster = cluster_from_args(args)
    logger.info(f"Parameters parsed, cluster is {cluster}")
    # Start the process of creating the cluster  
    create_cluster(project, cluster)
