# Description: This file contains the logic to update a cluster
import uuid
import os
from loguru import logger
from shared.entities.cluster import ClusterUpdateType
from shared.lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig, update_region_managed_instance_group,create_region_instance_group_managers_client, apply_updates_to_instances
from shared.lib.template import create_template, get_instance_template, update_template, create_instance_templates_client
from shared.lib.firewall import setup_firewall
from shared.lib.storage import setup_cloud_storage, upload_scripts
# from lib.secrets_manager import setup_secret_manager
from shared.discovery.secrets_manager import setup_secret_manager
# from lib.kms import setup_encryption_keys
from shared.discovery.kms import setup_encryption_keys
from shared.lib.images import get_image_from_family
from utils.exceptions import GCPManagedInstanceGroupNotFoundException, GCPInstanceTemplateAlreadyExistsException


def update_cluster(project, cluster, update_type: ClusterUpdateType):
    """
    Perform all the necessary operations in order to update a GCP couchbase cluster. This includes the following steps:
        - Check if the secret manager exists, if not create it
        - Check if the encryption key exists, if not create it
        - Check if the cloud storage bucket exists, if not create it
        - Upload the scripts to the cloud storage bucket
        - Check if the instance template exists, if not create it
        - Check if the managed instance group exists, if not create it
        - Check if the firewall rules exist, if not create them
    Parameters:
        project: The GCP project object
        cluster: The cluster parameters
        update_type: The type of update to perform
    """
    # check managed instance group 
    logger.info(f"Checking if managed instance group {cluster.name} exists ...")
    mig = get_region_managed_instance_group(project, cluster.region, cluster.name)
    if mig is None: 
        logger.info(f"Managed instance group {cluster.name} does not exist")
        logger.info("You will need to create a new instance group")
        raise GCPManagedInstanceGroupNotFoundException(f"Managed instance group {cluster.name} does not exist")
    else:
        logger.debug(f"Regional managed instance group {cluster.name} already exists")

        # checking secret manager
        logger.info("Checking secret manager ...")
        secret_name = setup_secret_manager(project, cluster, cluster.couchbase_params)

        # checking encryption keys
        logger.info("Checking encryption keys ...")
        key = setup_encryption_keys(project, cluster.name, cluster.region)

        # checking cloud storage
        logger.info("Checking cloud storage ...")
        bucket = setup_cloud_storage(project, cluster.storage, cluster.region, key)

        # upload scripts 
        logger.info("Uploading scripts ...")
        scripts = upload_scripts(project, bucket, cluster.template, cluster, secret_name)

        # setup instance template
        logger.info("Checking instance template ...")
        instance_template = setup_instance_template(project, cluster, cluster.template, cluster.storage, scripts, key)
        # update managed instance group 
        logger.info("Updating managed instance group ...")
        update_mig(project, cluster, instance_template, update_type)
    logger.info("Checking firewall rules ...")
    setup_firewall(project, cluster.name)
    logger.success(f"Cluster {cluster.name} updated successfully")









def setup_instance_template(project, cluster_params, template_params, storage_params, scripts_urls, encryption_key): 
    """
    Setup the instance template for the cluster
    """
    #Get the machine image from the project and family
    machine_image = get_image_from_family(project, template_params.image_project, template_params.image_family)

    template = get_instance_template(project, template_params.name)
    # check if there is a template existing 
    if template is None: 
        logger.info(f"Instance template {template_params.name} does not exist, creating ...")
        # create instance template
        template = create_template(
            project,
            template_params.name,
            template_params.machine_type,
            machine_image,
            template_params.disks,
            encryption_key,
            scripts_urls['startup_script_url'],
            scripts_urls['shutdown_script_url'],
            template.labels
        )
    else:
        logger.debug(f"Instance template {template_params.name} already exists")
        logger.error("To update the cluster we would need to create a new instance template with new name ")
        raise GCPInstanceTemplateAlreadyExistsException(f"Instance template {template_params.name} already exists, To update the cluster we would need to create a new instance template with new name ")
    return template



def update_mig(project, cluster, template, update_type: ClusterUpdateType):
    """
    Update the regional managed instance group
    """
    logger.debug(f"Updating regional managed instance group {cluster.name}")
    mig = update_region_managed_instance_group(project, cluster.region, cluster.name, template) 
    logger.debug(f"Regional managed instance group {cluster.name} updated")
    if update_type == ClusterUpdateType.UPDATE_AND_MIGRATE: 
        # applying updates to the instances 
        logger.debug(f"Applying updates in a rolling manner to the instances in regional managed instance group {cluster.name}")
        apply_updates_to_instances(project, cluster.region, mig)
        logger.debug(f"Scaling regional managed instance group {cluster.name} to {cluster.size}")
    region_scaling_mig(project, cluster.region, mig, mig.target_size, cluster.size)

