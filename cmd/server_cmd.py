import os 
import base64
from api import create_app
from loguru import logger

def start_server(args): 
    logger.info("Welcome to the server sub command ")
    # setting flask server configuration 
    logger.info("Setting flask server configuration ...")
    # create and configure the app
    app = create_app()
    # start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
    
