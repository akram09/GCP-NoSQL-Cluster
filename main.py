from utils.env import load_project_env
from utils.args import parse_args, cluster_from_args
from loguru import logger


if __name__ == "__main__": 
    # set the log level to debug
    project = load_project_env()
    # initialize cluster 
    args = parse_args()
    cluster = cluster_from_args(args)
    # deploy cluster on gcp
    cluster.deploy_cluster_gcp(project) 
