from loguru import logger
from utils.shared import check_gcp_params
from utils.args import cluster_from_args
from core.create_cluster import create_cluster



def create_cluster(args):
    logger.info("Welcome to the cluster creation script")
    logger.info("Checking parameters ...")
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")

    # parse parameters 
    logger.info("Parsing parameters ...")
    cluster = cluster_from_args(args)
    logger.info(f"Parameters parsed, cluster is {cluster}")
    
    create_cluster(project, cluster)
