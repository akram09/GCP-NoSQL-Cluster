import os
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_args
from lib.managed_instance import create_managed_instance_group

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
    print(args)

    # Create a managed instance group 
    create_managed_instance_group(project_id, zone, "mig-1", "template-sample-1")
    
