
# GCP project class for the GCP project that hosts the cluster.
class GCPProject:
    def __init__(self, project_id, zone, compute_engine_service_account):
        self.project_id = project_id
        self.zone = zone
        self.compute_engine_service_account = compute_engine_service_account

    # print str of the GCP project
    def __str__(self):
        return f"project_id: {self.project_id}, zone: {self.zone}, compute_engine_service_account: {self.compute_engine_service_account}"
