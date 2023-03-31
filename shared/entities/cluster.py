from enum import Enum

class ClusterParams:

    def __init__(self, cluster_name, cluster_size, cluster_region, storage=None, template=None, couchbase_params=None):
        self.name = cluster_name
        self.size = cluster_size
        self.region = cluster_region
        self.template = template
        self.storage = storage
        self.couchbase_params = couchbase_params
    
    # print cluster details
    def __str__(self):
        return f"Cluster {self.name} with {self.size} nodes, storage {self.storage}, template {self.template}, couchbase params {self.couchbase_params}"

class ClusterUpdateType(Enum):
    UPDATE_AND_MIGRATE = 1
    UPDATE_NO_MIGRATE = 2
