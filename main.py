import os, uuid
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_args, ClusterArgs
from lib.managed_instance import create_managed_instance_group, create_couchbase_cluster create_cluster
from lib.template import list_instance_templates, delete_instance_template, get_instance_template
from lib.vm_instance import create_instance_from_template, delete_instance


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

    # parse arguments
    args = parse_args()


    cluster_args = ClusterArgs(args)

    create_cluster(project_id, zone, cluster_args)
    
