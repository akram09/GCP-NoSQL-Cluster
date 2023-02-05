from utils.env import get_env_project_id, check_application_credentials, check_compute_engine_service_account_email, check_storage_service_account_email 
from loguru import logger
from entities.gcp_project import GCPProject

# Check parameters
def check_gcp_params(args):
    # check project id 
    if args.project_id is None:
        logger.info("Project ID not provided in command line arguments")
        logger.info("Checking environment variables")
        try:
            args.project_id = get_env_project_id()
        except Exception as e:
            logger.error(e)
            exit(1)
    # check compute service account 
    try:
        check_compute_engine_service_account_email()
    except Exception as e:
        logger.error(e)
        exit(1)

    # check storage service account
    try:
        check_storage_service_account_email()
    except Exception as e:
        logger.error(e)
        exit(1)

    # check authentication 
    if args.authentication_type == "service-account":
        logger.info("Authentication type set to use service account")
        logger.info("Checking environment variable")
        try:
            check_application_credentials()
        except Exception as e:
            logger.error(e)
            exit(1)
    elif args.authentication_type == "oauth":
        logger.error("OAuth authentication not implemented yet")
        exit(1)


    return  GCPProject(args.project_id)