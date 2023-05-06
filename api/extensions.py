from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from api.internal.couchbase import CouchbaseCluster




bcrypt = Bcrypt()
db = SQLAlchemy()
couchbase = CouchbaseCluster()
