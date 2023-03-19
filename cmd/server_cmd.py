import os 
import base64
from api import create_app
from loguru import logger

def start_server(args): 
    logger.info("Welcome to the server sub command ")
    # setting flask server configuration 
    logger.info("Setting flask server configuration ...")
    app_config = {
        'ENV': 'development',
        'SECRET_KEY': base64.b64encode(os.urandom(24)).decode('utf-8')
    }
    # create and configure the app
    app = create_app(app_config)
    # start the server
    app.run(host=args.host, port=args.port, debug=args.debug)
    
