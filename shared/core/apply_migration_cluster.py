# Description: This file contains the functions to apply the migration to the cluster
import uuid
import os
from loguru import logger
from shared.lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig, update_region_managed_instance_group,create_region_instance_group_managers_client, apply_updates_to_instances
from utils.exceptions import GCPManagedInstanceGroupNotFoundException


def apply_migration(project, cluster_name, cluster_region):
    """
    Apply the migration to the cluster. 
    Parameters:
        project: The project id
        cluster_name: The name of the cluster
        cluster_region: The region of the cluster
    Returns: 
        None
    """
    # check managed instance group 
    logger.info(f"Checking if managed instance group {cluster_name} exists ...")
    mig = get_region_managed_instance_group(project, cluster_region, cluster_name)
    if mig is None: 
        logger.info(f"Managed instance group {cluster_name} does not exist")
        logger.info("You will need to create a new instance group")
        raise GCPManagedInstanceGroupNotFoundException(f"Managed instance group {cluster_name} does not exist")
    else:
        logger.debug(f"Regional managed instance group {cluster_name} already exists")

        # update managed instance group 
        logger.info("Updating managed instance group ...")
        migrate_mig(project, cluster_region, mig)
    logger.success(f"Cluster {cluster_name} migrated successfully")





def migrate_mig(project, cluster_region, mig):
    # applying updates to the instances 
    logger.debug(f"Applying updates in a rolling manner to the instances in regional managed instance group ")
    apply_updates_to_instances(project, cluster_region, mig)

