import os 
import base64
from api import create_app
from loguru import logger
from utils.shared import check_gcp_params

def start_server(args): 
    logger.info("Welcome to the server sub command ")
    logger.info("Checking parameters ...")
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")
    # setting flask server configuration 
    logger.info("Setting flask server configuration ...")
    app_config = {
        'ENV': 'development',
        'SECRET_KEY': base64.b64encode(os.urandom(24)).decode('utf-8')
    }
    # create and configure the app
    app = create_app(project, app_config)
    # start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
    
