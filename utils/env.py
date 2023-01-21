from loguru import logger
from dotenv import load_dotenv
import os 
from entities.gcp_project import GCPProject


def init(): 
    # load environment variables from .env file
    load_dotenv()

# get project id from environment variables
def get_env_project_id(): 
    if "GOOGLE_CLOUD_PROJECT" not in os.environ:
        raise Exception("Please set GOOGLE_CLOUD_PROJECT environment variable")
    else:
        if os.environ.get("GOOGLE_CLOUD_PROJECT") =="":
            raise Exception("GOOGLE_CLOUD_PROJECT environment variable is empty")
        return os.environ.get("GOOGLE_CLOUD_PROJECT") 



# checking application credentials
def check_application_credentials():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise Exception("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    else:
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") =="":
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable is empty")

# checking compute engine service account email
def check_compute_engine_service_account_email():
    if "COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL" not in os.environ:
        raise Exception("Please set COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL environment variable")
    else:
        if os.environ.get("COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL") =="":
            raise Exception("COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL environment variable is empty")


def load_project_env():
    # check environment variables
    try:
        check_env()
    except Exception as e:
        logger.error(e)
        exit(1)
    # get environment variables
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    zone = os.environ.get("GOOGLE_CLOUD_ZONE")
    compute_engine_service_account = os.environ.get("COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL")

    return GCPProject(project, zone, compute_engine_service_account)

    
