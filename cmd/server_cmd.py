"""
This module allows to start a REST API server that exposes the cluster management operations.
"""
import os 
import base64
from api import create_app
from loguru import logger

def start_server(args): 
    """
    Start a REST API server that exposes the cluster management operations.
    """
    logger.info("Welcome to the server sub command ")
    # setting flask server configuration 
    logger.info("Setting flask server configuration ...")
    # create and configure the app
    app = create_app()
    # start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
    
