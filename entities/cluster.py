class ClusterParams:

    def __init__(self, cluster_name, cluster_size, storage=None, template=None, couchbase_params=None):
        self.cluster_name = cluster_name
        self.cluster_size = cluster_size
        self.template = template
        self.storage = storage
        self.couchbase_params = couchbase_params
    
    # print cluster details
    def __str__(self):
        return f"Cluster {self.cluster_name} with {self.cluster_size} nodes, storage {self.storage}, template {self.template}, couchbase params {self.couchbase_params}"

