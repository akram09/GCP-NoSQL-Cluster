from utils.env import get_env_project_id, check_application_credentials
from loguru import logger

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
