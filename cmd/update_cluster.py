import uuid
import os
from loguru import logger
from utils.shared import check_gcp_params
from utils.args import cluster_from_args
from shared.lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig, update_region_managed_instance_group,create_region_instance_group_managers_client, apply_updates_to_instances
from shared.lib.template import create_template, get_instance_template, update_template, create_instance_templates_client
from shared.lib.firewall import setup_firewall
from shared.lib.storage import setup_cloud_storage, upload_scripts
# from lib.secrets_manager import setup_secret_manager
from shared.discovery.secrets_manager import setup_secret_manager
# from lib.kms import setup_encryption_keys
from shared.discovery.kms import setup_encryption_keys
from shared.lib.images import get_image_from_family



def update_cluster(args):
    logger.info("Welcome to the cluster update  script")
    logger.info("Checking parameters ...")
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")

    # parse parameters 
    logger.info("Parsing parameters ...")
    cluster = cluster_from_args(args)
    logger.info(f"Parameters parsed, cluster is {cluster}")

    # check managed instance group 
    logger.info(f"Checking if managed instance group {cluster.name} exists ...")
    mig = get_region_managed_instance_group(project, cluster.region, cluster.name)
    if mig is None: 
        logger.info(f"Managed instance group {cluster.name} does not exist")
        logger.info("You will need to create a new instance group")
        exit(1)
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
        update_mig(project, cluster, instance_template)
    logger.info("Checking firewall rules ...")
    setup_firewall(project, cluster.name)
    logger.success(f"Cluster {cluster.name} updated successfully")









def setup_instance_template(project, cluster_params, template_params, storage_params, scripts_urls, encryption_key): 
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
            scripts_urls['shutdown_script_url']
        )
    else:
        logger.debug(f"Instance template {template_params.name} already exists")
        logger.error("To update the cluster we would need to create a new instance template with new name ")
        exit(1)
    return template



def update_mig(project, cluster, template):
    logger.debug(f"Updating regional managed instance group {cluster.name}")
    mig = update_region_managed_instance_group(project, cluster.region, cluster.name, template) 
    logger.debug(f"Regional managed instance group {cluster.name} updated")
    # applying updates to the instances 
    logger.debug(f"Applying updates in a rolling manner to the instances in regional managed instance group {cluster.name}")
    apply_updates_to_instances(project, cluster.region, mig)
    logger.debug(f"Scaling regional managed instance group {cluster.name} to {cluster.size}")
    region_scaling_mig(project, cluster.region, mig, mig.target_size, cluster.size)

