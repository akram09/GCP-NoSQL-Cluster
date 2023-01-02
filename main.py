from utils.env import check_env
import os
from lib.managed_instance import create_managed_instance_group

if __name__ == "__main__":
    # check environment variables 
    check_env()

    # TODO 1: migrate to argparse
    # get project id
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    # get zone
    zone = os.environ["GOOGLE_CLOUD_ZONE"]

    # Create a managed instance group 
    create_managed_instance_group(project_id, zone, "mig-1", "template-sample-1")
    
