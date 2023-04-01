import os
from flask import Flask, g, Blueprint
from flask_restx import Api
from api.routes.cluster import api as cluster_api
from api.routes.job import api as job_api
from api.routes.auth import api as auth_api
from api.config import Config
from api.extensions import db, bcrypt


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




def create_app(test_config=None):
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
        db.create_all()
    bcrypt.init_app(app)
    # register the cluster blueprint
    app.register_blueprint(api_blueprint)
    return app



