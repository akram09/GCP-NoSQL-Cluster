"""
This file is used to initialize the flask app and register the blueprints, the api and the extensions.
"""
import os
from flask import Flask, g, Blueprint
from flask_restx import Api
from api.routes.cluster import api as cluster_api
from api.routes.job import api as job_api
from api.routes.auth import api as auth_api
from api.routes.template import api as template_api
from api.routes.managed_instance import api as managed_instance_api
from api.routes.kms import api as kms_api
from api.routes.storage import api as storage_api
from api.config import Config
from api.extensions import db, bcrypt, couchbase


# create the api blueprint 
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# create the api
api = Api(api_blueprint, version='1.0', title='GCP Cluster API', description='A simple API to create GCP clusters')

# add the cluster namespace to the api
api.add_namespace(cluster_api)
# add the job namespace to the api
api.add_namespace(job_api)
# add auth namespace to the api
api.add_namespace(auth_api)
# add template namespace to the api
api.add_namespace(template_api)
# add managed instance namespace to the api_blueprint
api.add_namespace(managed_instance_api)
# add kms namespace to the api_blueprint
api.add_namespace(kms_api)
# add storage namespace to the api_blueprint
api.add_namespace(storage_api)





def create_app(test_config=None):
    """
    Create and configure an instance of the Flask application.
    Parameters:
        test_config: the configuration to use when testing the application. Default is None.
    Returns:
        app: the Flask application instance.
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
   
    # initialize extensions
    db.init_app(app)
    with app.app_context():
        # create db tables if they don't exist yet
        db.create_all()
    bcrypt.init_app(app)
    couchbase.init_couchbase()
    # register the cluster blueprint
    app.register_blueprint(api_blueprint)
    return app



