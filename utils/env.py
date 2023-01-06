from dotenv import load_dotenv
import os 

# check environment variables 
def check_env():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise Exception("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    if "GOOGLE_CLOUD_PROJECT" not in os.environ:
        raise Exception("Please set GOOGLE_CLOUD_PROJECT environment variable")
    if "GOOGLE_CLOUD_ZONE" not in os.environ:
        raise Exception("Please set GOOGLE_CLOUD_ZONE environment variable")
    if "COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL" not in os.environ:
        raise Exception("Please set COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL environment variable, this will allow the instances to fetch the scripts from cloud storage")


def load_project_env():
    # load environment variables from .env file
    load_dotenv()
    # check environment variables
    check_env()
    # get environment variables
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    zone = os.environ.get("GOOGLE_CLOUD_ZONE")
    compute_engine_service_account = os.environ.get("COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL")

    return GCPProject(project, zone, compute_engine_service_account)

    
