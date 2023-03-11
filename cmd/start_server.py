from api import create_app
from loguru import logger
from utils.shared import check_gcp_params

def start_server(args): 
    logger.info("Welcome to the cluster update  script")
    logger.info("Checking parameters ...")
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")
    # create and configure the app
    app = create_app(project, args)
    # start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
    
