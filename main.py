import os, uuid
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_cluster_args
from cluster.cluster import ClusterArgs
from lib.managed_instance import create_cluster 


if __name__ == "__main__":
    # parse arguments
    args = parse_cluster_args()

    # load environment variables
    load_dotenv()
    # check environment variables 
    check_env()

    # get project id
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    # get zone
    zone = os.environ["GOOGLE_CLOUD_ZONE"]

    cluster_args = ClusterArgs(args)

    create_cluster(project_id, zone, cluster_args)
    
