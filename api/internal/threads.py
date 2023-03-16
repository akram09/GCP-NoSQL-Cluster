from loguru import logger
import threading 
from core.create_cluster import create_cluster
from core.update_cluster import update_cluster
from utils.exceptions import InternalException
from api.cache import update_job_status

class CreateClusterThread(threading.Thread):
    def __init__(self, job_id, gcp_project, cluster):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.cluster = cluster

    def run(self):
        try:
            create_cluster(self.gcp_project, self.cluster)
        except InternalException as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error creating the cluster: {e}")

class UpdateClusterThread(threading.Thread):
    def __init__(self, job_id, gcp_project, cluster):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.cluster = cluster

    def run(self):
        try:
            update_cluster(self.gcp_project, self.cluster)
        except InternalException as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error updating the cluster: {e}")
