from loguru import logger
import threading 
from shared.core.create_cluster import create_cluster
from shared.core.update_cluster import update_cluster
from shared.core.apply_migration_cluster import apply_migration
from shared.entities.cluster import ClusterUpdateType
from utils.exceptions import InternalException
from api.internal.cache import update_job_status
from shared.lib.template import create_template, update_template

class AsyncOperationThread(threading.Thread): 
    def __init__(self, job_id, gcp_project, operation, **operation_params):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.operation = operation
        self.operation_params = operation_params

    def run(self):
        try:
            self.operation(self.gcp_project, **self.operation_params)
            update_job_status(self.name, 'COMPLETED')
        except InternalException as e:
            if e.message:
                update_job_status(self.name, 'FAILED', e.message)
            else:
                update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Internal Error: {e}")
        except Exception as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error: {e}")




class CreateClusterThread(threading.Thread):
    def __init__(self, job_id, gcp_project, cluster):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.cluster = cluster

    def run(self):
        try:
            create_cluster(self.gcp_project, self.cluster)
            update_job_status(self.name, 'COMPLETED')
        except InternalException as e:
            if e.message:
                update_job_status(self.name, 'FAILED', e.message)
            else:
                update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Internal Error creating the cluster: {e}")
        except Exception as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error creating the cluster: {e}")

class UpdateClusterThread(threading.Thread):
    def __init__(self, job_id, gcp_project, cluster, cluster_update_type):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.cluster = cluster
        self.cluster_update_type = cluster_update_type

    def run(self):
        try:
            update_cluster(self.gcp_project, self.cluster, self.cluster_update_type)
            update_job_status(self.name, 'COMPLETED')
        except InternalException as e:
            if e.message:
                update_job_status(self.name, 'FAILED', e.message)
            else:
                update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error updating the cluster: {e}")
        except Exception as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error updating the cluster: {e}")

class MigrateClusterThread(threading.Thread):
    def __init__(self, job_id, gcp_project, cluster_name, cluster_region):
        threading.Thread.__init__(self)
        self.name = job_id
        self.gcp_project = gcp_project
        self.cluster_name = cluster_name
        self.cluster_region = cluster_region


    def run(self):
        try:
            apply_migration(self.gcp_project, self.cluster_name, self.cluster_region)
            update_job_status(self.name, 'COMPLETED')
        except InternalException as e:
            if e.message:
                update_job_status(self.name, 'FAILED', e.message)
            else:
                update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error updating the cluster: {e}")
        except Exception as e:
            update_job_status(self.name, 'FAILED')
            # log the error
            logger.error(f"Error updating the cluster: {e}")

