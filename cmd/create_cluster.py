from loguru import logger
from utils.shared import check_gcp_params
from utils.args import cluster_from_args
from lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig
from lib.template import create_template, get_instance_template, update_template
from lib.firewall import create_firewall_rule, check_firewall_rule
from lib.storage import upload_startup_script, upload_shutdown_script
from lib.secrets_manager import check_secret, create_secret, add_latest_secret_version
from utils.gcp import get_image_from_family



def create_cluster(args):
    logger.info("Welcome to the cluster creation script")
    logger.info("Checking parameters ...")
    project = check_gcp_params(args)
    logger.info(f"Parameters checked, project is {project}")

    # parse parameters 
    logger.info("Parsing parameters ...")
    cluster = cluster_from_args(args)
    logger.info(f"Parameters parsed, cluster is {cluster}")

    # check managed instance group 
    logger.info(f"Checking if managed instance group {cluster.name} exists ...")
    mig = get_region_managed_instance_group(project.project_id, cluster.region, cluster.name)
    if mig is None: 
        logger.info(f"Managed instance group {cluster.name} does not exist")

        # checking secret manager
        logger.info("Checking secret manager ...")
        setup_secret_manager(project, cluster, cluster.couchbase_params)

        # setup instance template
        logger.info("Checking instance template ...")
        instance_template = setup_instance_template(project, cluster, cluster.template, cluster.storage)
        

        # create managed instance group
        logger.info("Creating managed instance group ...")
        create_mig(project, cluster, instance_template)

    else:
        logger.debug(f"Regional managed instance group {cluster.name} already exists")
        # setup instance template
        logger.info("Checking instance template ...")
        instance_template = setup_instance_template(project, cluster, cluster.template, cluster.storage)
        logger.info(f"Scaling managed instance group {cluster.name} to {cluster.size} instances ...")
        scale_mig(project, cluster, mig)

    logger.info("Checking firewall rules ...")
    setup_firewall(project, cluster.name)
    logger.success(f"Cluster {cluster.name} created successfully")



def setup_secret_manager(project, cluster, couchbase_params):

    # admin password secret
    secret_name = f"{cluster.name}-admin-creds"

    # check if the params are not null
    if couchbase_params is  None:
        logger.info(f"Couchbase credentials not specified, we will check if the secret already exists")
        secret = check_secret(project.project_id, secret_name)
        if secret is None:
            logger.info("Couchbase secret don't exists ")
            exit(1)
        else:
            logger.info("Couchbase secret already exists")
            logger.info(f"The cluster will use the 'latest' version of secret {secret}")
    else:    
        logger.info(f"Couchbase credentials specified, we will check if the secret already exists")
        secret = check_secret(project.project_id, secret_name)
        if secret is None:
            logger.info("Creating secret manager for admin creds ...")
            secret = create_secret(project.project_id, secret_name)
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            add_latest_secret_version(project.project_id, secret_name, admin_creds)
        else:
            logger.info("Secret already exists, therefore we will update the 'latest' version")
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            add_latest_secret_version(project.project_id, secret_name, admin_creds)


def scale_mig(project, cluster, mig):
    # scaling mig
    region_scaling_mig(project.project_id, cluster.region, mig, mig.target_size, cluster.size)


def setup_instance_template(project, cluster_params, template_params, storage_params): 
    #Get the machine image from the project and family
    machine_image = get_image_from_family(template_params.image_project, template_params.image_family)
    # upload the startup script to the bucket
    startup_script_url = upload_startup_script(project.project_id, template_params.image_family, storage_params.bucket, cluster_params.name, cluster_params.size)
    # upload the shutdown script to the bucket
    shutdown_script_url = upload_shutdown_script(project.project_id, template_params.image_family, storage_params.bucket)

    template = get_instance_template(project.project_id, template_params.name)
    # check if there is a template existing 
    if template is None: 
        logger.info(f"Instance template {template_params.name} does not exist, creating ...")
        # create instance template
        template = create_template(
            project.project_id,
            template_params.name,
            template_params.machine_type,
            machine_image,
            template_params.disks,
            startup_script_url, 
            shutdown_script_url
        )
    else:
        logger.debug(f"Instance template {template_params.name} already exists")
        # update the instance template 
        update_template(
            project.project_id,
            template,
            template_params.machine_type,
            machine_image,
            template_params.disks,
            startup_script_url, 
            shutdown_script_url
        )
    return template



def create_mig(project, cluster, template):
    logger.debug(f"Creating regional managed instance group {cluster.name}")
    mig = create_region_managed_instance_group(project.project_id, cluster.region, cluster.name, template)
    region_adding_instances(project.project_id, cluster.region, mig, cluster.size)
    

def setup_firewall(project, cluster_name):
    # Check if the firewall rule exists
    if check_firewall_rule(project.project_id, cluster_name+"-firewall"):
        logger.debug(f"Firewall rule {cluster_name}-firewall already exists")
    else:
        logger.debug(f"Creating firewall rule {cluster_name}-firewall")
        create_firewall_rule(project.project_id, cluster_name+"-firewall")
        logger.success(f"Firewall rule {cluster_name}-firewall created")
