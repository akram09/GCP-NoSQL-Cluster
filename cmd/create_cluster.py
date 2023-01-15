from loguru import logger
from utils.shared import check_gcp_params

def create_cluster(args):
    logger.info("Welcome to the cluster creation script")
    logger.info("Checking parameters ...")
    check_gcp_params(args)
    




        
