import uuid
import os
from loguru import logger
from utils.shared import check_gcp_params
from utils.args import cluster_from_args
from lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig, update_region_managed_instance_group,create_region_instance_group_managers_client 
from lib.template import create_template, get_instance_template, update_template, create_instance_templates_client
from lib.firewall import create_firewall_rule, check_firewall_rule, create_firewalls_client
from lib.storage import upload_startup_script, upload_shutdown_script, create_bucket, create_storage_client
from lib.secrets_manager import check_secret, create_secret, add_latest_secret_version, create_secret_manager_client
from lib.kms import create_key_ring, create_key_symmetric_encrypt_decrypt, get_key_ring, get_key_symmetric_encrypt_decrypt, is_key_enabled, create_key_management_service_client
from utils.gcp import get_image_from_family



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
    client = create_region_instance_group_managers_client(project)
    mig = get_region_managed_instance_group(client, project.project_id, cluster.region, cluster.name)
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
        update_mig(client, project, cluster, instance_template)
    logger.info("Checking firewall rules ...")
    setup_firewall(project, cluster.name)
    logger.success(f"Cluster {cluster.name} updated successfully")



def setup_encryption_keys(project, cluster_name, region):

    # create secret manager client
    client = create_key_management_service_client(project)

    # Create KMS key ring and symmetric encryption/decryption key
    key_ring_id = f"key-ring-{cluster_name}" 
    logger.info(f"Checking key ring {key_ring_id} ...")
    # check if key ring exists 
    key_ring = get_key_ring(client, project.project_id, region, key_ring_id)
    if key_ring is None: 
        logger.debug("Key ring does not exist, creating key ring")
        key_ring = create_key_ring(client, project.project_id, region, key_ring_id)

    logger.info("Checking encryption key ...")
    key_id = f"key-{cluster_name}"
    key = create_key_symmetric_encrypt_decrypt(client, project.project_id, region, key_ring_id, key_id+f"-{uuid.uuid4().hex}")
    return key



def setup_secret_manager(project, cluster, couchbase_params):

    # admin password secret
    secret_name = f"{cluster.name}-admin-creds"
    # create secret manager client
    client = create_secret_manager_client(project)

    # check if the params are not null
    if couchbase_params is  None:
        logger.info(f"Couchbase credentials not specified, we will check if the secret already exists")
        secret = check_secret(client, project.project_id, secret_name)
        if secret is None:
            logger.info("Couchbase secret don't exists ")
            exit(1)
        else:
            logger.info("Couchbase secret already exists")
            logger.info(f"The cluster will use the 'latest' version of secret {secret}")
    else:    
        logger.info(f"Couchbase credentials specified, we will check if the secret already exists")
        secret = check_secret(client, project.project_id, secret_name)
        if secret is None:
            logger.info("Creating secret manager for admin creds ...")
            secret = create_secret(client, project.project_id, secret_name)
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            add_latest_secret_version(client, project.project_id, secret_name, admin_creds)
        else:
            logger.info("Secret already exists, therefore we will update the 'latest' version")
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            add_latest_secret_version(client, project.project_id, secret_name, admin_creds)
    return secret_name





def upload_scripts(project, bucket, template_params, cluster_params, secret_name):
    # create storage client 
    client = create_storage_client(project)

    # upload the startup script to the bucket
    startup_script_url = upload_startup_script(client, project.project_id, template_params.image_family, bucket, cluster_params.name, cluster_params.size, secret_name)
    # upload the shutdown script to the bucket
    shutdown_script_url = upload_shutdown_script(client, project.project_id, template_params.image_family, bucket)

    return {
        "startup_script_url": startup_script_url,
        "shutdown_script_url": shutdown_script_url
    }



def setup_instance_template(project, cluster_params, template_params, storage_params, scripts_urls, encryption_key): 
    # create client 
    client = create_instance_templates_client(project)

    #Get the machine image from the project and family
    machine_image = get_image_from_family(template_params.image_project, template_params.image_family)

    template = get_instance_template(client, project.project_id, template_params.name)
    # check if there is a template existing 
    if template is None: 
        logger.info(f"Instance template {template_params.name} does not exist, creating ...")
        # create instance template
        template = create_template(
            client,
            project.project_id,
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


def setup_cloud_storage(project, storage_params, region, key):
    # Create storage client
    storage_client = create_storage_client(project)

    logger.info("Checking if the bucket exists else creating the bucket...")
    # Create the bucket if not existed
    bucket = create_bucket(storage_client, storage_params.bucket, region, key)

    logger.info("Assigning read storage role to the bucket...") 
    # Add Compute Engine default service account to the bucket
    # read member from environment variable
    member = {"user": os.environ['COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL']}
    role = "roles/storage.objectViewer"

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": [member]})

    bucket.set_iam_policy(policy)
    logger.debug(f"Added {member} to {bucket.name} with {role} role.")

    return bucket

def update_mig(client, project, cluster, template):
    logger.debug(f"Updating regional managed instance group {cluster.name}")
    mig = update_region_managed_instance_group(client, project.project_id, cluster.region, cluster.name, template) 
    region_scaling_mig(client, project.project_id, cluster.region, mig, mig.target_size, cluster.size)






def setup_firewall(project, cluster_name):
    # create client 
    client = create_firewalls_client(project)

    # Check if the firewall rule exists
    if check_firewall_rule(client, project.project_id, cluster_name+"-firewall"):
        logger.debug(f"Firewall rule {cluster_name}-firewall already exists")
    else:
        logger.debug(f"Creating firewall rule {cluster_name}-firewall")
        create_firewall_rule(client, project.project_id, cluster_name+"-firewall")
        logger.success(f"Firewall rule {cluster_name}-firewall created")
