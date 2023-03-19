import os
from flask import Flask, g, Blueprint
from flask_restx import Api
from api.routes.cluster import api as cluster_api
from api.routes.job import api as job_api


# create the api blueprint 
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# create the api
api = Api(api_blueprint, version='1.0', title='GCP Cluster API', description='A simple API to create GCP clusters')

# add the cluster namespace to the api
api.add_namespace(cluster_api)
# add the job namespace to the api
api.add_namespace(job_api)




def create_app(gcp_project, test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
   
    # store a global object that can be accessed in all requests
    @app.before_request
    def before_request():
        g.gcp_project = gcp_project

    # register the cluster blueprint
    app.register_blueprint(api_blueprint)
    return app



