import os, uuid
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_args, ClusterArgs
from lib.managed_instance import create_cluster


if __name__ == "__main__":
    # load environment variables
    load_dotenv()
    # check environment variables 
    check_env()

    # get project id
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    # get zone
    zone = os.environ["GOOGLE_CLOUD_ZONE"]

    # parse arguments
    args = parse_args()


    #delete_all_templates(project_id);exit()

    cluster_args = ClusterArgs(args)
    #print(cluster_args)

    # Create a managed instance group 
    create_cluster(project_id, zone, cluster_args)
    
