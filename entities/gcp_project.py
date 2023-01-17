
# GCP project class for the GCP project that hosts the cluster.
class GCPProject:
    def __init__(self, project_id, auth_type="service-account"):
        self.project_id = project_id
        self.auth_type = auth_type

    # print str of the GCP project
    def __str__(self):
        return f"GCPProject(project_id={self.project_id}, auth_type={self.auth_type})"
