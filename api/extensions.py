# Description: This file contains the extensions used by the application.

from flask_bcrypt import Bcrypt
from api.internal.couchbase import CouchbaseCluster


bcrypt = Bcrypt()
couchbase = CouchbaseCluster()
