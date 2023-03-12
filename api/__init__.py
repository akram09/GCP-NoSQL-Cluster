import os
from flask import Flask, g
import api.cluster as cluster

def create_app(gcp_project, test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    with app.app_context():
        # set the gcp project in the global g 
        g.gcp_project = gcp_project

    # register the cluster blueprint
    app.register_blueprint(cluster.bp)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app
