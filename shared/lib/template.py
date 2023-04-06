from loguru import logger
from google.cloud import compute_v1
from utils.shared import wait_for_extended_operation
from shared.lib.disks import  disk_from_image
from typing import Iterable
from shared.lib.kms import create_key_ring, create_key_symmetric_encrypt_decrypt, get_key_ring, get_key_symmetric_encrypt_decrypt, is_key_enabled
import os
import google.oauth2.credentials



# public function 
def create_template(project, template_name, machine_type, machine_image, disks, key, startup_script_url, shutdown_script_url, tags):
    client = create_instance_templates_client(project)
    return __create_template(client, project.project_id, template_name, machine_type, machine_image, disks, key, startup_script_url, shutdown_script_url, tags)



# public function 
def update_template(project, template_name, machine_type, machine_image, disks, key, startup_script_url, shutdown_script_url, tags):
    client = create_instance_templates_client(project)
    return __update_template(client, project.project_id, template_name, machine_type, machine_image, disks, key, startup_script_url, shutdown_script_url, tags)



# public function 
def get_instance_template(project, template_name):
    client = create_instance_templates_client(project)
    return __get_instance_template(client, project.project_id, template_name)

# public function 
def list_instance_templates(project):
    client = create_instance_templates_client(project)
    return __list_instance_templates(client, project.project_id)

# public function 
def delete_instance_template(project, template_name):
    client = create_instance_templates_client(project)
    return __delete_instance_template(client, project.project_id, template_name)

# public function 
def delete_all_templates(project):
    client = create_instance_templates_client(project)
    return __delete_all_templates(client, project.project_id)



# create instance templates client 
def create_instance_templates_client(project): 
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return compute_v1.InstanceTemplatesClient(credentials=credentials)
    # create the instance templates client
    return compute_v1.InstanceTemplatesClient()


def __create_template(
    client,
    project_id: str,
    template_name: str,
    machine_type: str,
    machine_image: compute_v1.types.compute.Image,
    disks, 
    key,
    startup_script_url: str,
    shutdown_script_url: str,
    labels
    ):
    """
    Create a new instance template with the provided name and a specific
    instance configuration.
    Args:
        project_id: project ID or project number of the Cloud project you use.
        template_name: name of the new template to create.
    Returns:
        InstanceTemplate object that represents the new instance template.
    """
    logger.info("Creating instance template...") 

    # The template connects the instance to the `default` network,
    # without specifying a subnetwork.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"

    # This template has a public ip 
    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type_ = "ONE_TO_ONE_NAT"
    access_config.network_tier = "PREMIUM"
    network_interface.access_configs = [access_config]


    template = compute_v1.InstanceTemplate()
    template.name = template_name
    # create instance tags 
    tags = compute_v1.Tags()
    tags.items = ["couchbase-server"]
    template.properties.tags = tags 
    template.properties.machine_type = machine_type
    template.properties.network_interfaces = [network_interface]

    # setting labels
    template.properties.labels  = labels

    # setting disks
    template_disks = list(map(lambda disk_params: disk_from_image(disk_params.type, disk_params.size, key, disk_params.boot, machine_image.self_link) , disks))
    template.properties.disks =  template_disks
    # get email from COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL environment variable
    email = os.environ["COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL"]
    #set scopes in serviceaccounts
    service_account = compute_v1.ServiceAccount()
    service_account.email = email
    service_account.scopes = [
        "https://www.googleapis.com/auth/devstorage.read_only",
        # secrets access 
        "https://www.googleapis.com/auth/cloud-platform"
    ]
    template.properties.service_accounts = [service_account]
    # set the startup script url in the metadata
    metadata = compute_v1.Metadata()
    metadata.items = [
        {
            "key": "startup-script-url",
            "value": startup_script_url
        },
        {
            "key": "shutdown-script-url",
            "value": shutdown_script_url
        },
        # use global dns 
        {
            "key": "VmDnsSetting",
            "value": "global"
        }
    ]
    template.properties.metadata = metadata


    operation = client.insert(
        project=project_id, instance_template_resource=template
    )

    wait_for_extended_operation(operation, "instance template creation")
    logger.success("Instance template created!")

    return client.get(project=project_id, instance_template=template_name)




# update template 
def __update_template(
    template_client,
    project_id: str,
    template: compute_v1.InstanceTemplate,
    machine_type: str,
    machine_image: compute_v1.types.compute.Image,
    disks_params,    
    key,
    startup_script_url: str,
    shutdown_script_url: str,
    labels
    ) -> compute_v1.InstanceTemplate:

    logger.info(f"Updating instance template {template.name}...")
    logger.info(f"Because gcp doesn't support updating an instance template we will delete the first and create new one with updated values")
    

    # delete the old template 
    operation = template_client.delete(project=project_id, instance_template=template.name)
    try:
        wait_for_extended_operation(operation, "deleting old instance template")
    except Exception as e:
        logger.warning("Failed to delete old instance template, the template is already in use")
        return template


    # check disks 
    disks = template.properties.disks

    # create list of new disks 
    new_disks = list(map(lambda disk_params: disk_from_image(disk_params.type, disk_params.size, key, disk_params.boot, machine_image.self_link) , disks_params))

    # compare disks 
    for i,disk in enumerate(disks):
        # check the boot disk properties 
        if disk.initialize_params.source_image != new_disks[i].initialize_params.source_image:
            logger.debug("Boot disk image is different, updating boot disk image")
            disk.initialize_params.source_image = new_disks[i].initialize_params.source_image
        if disk.initialize_params.disk_size_gb != new_disks[i].initialize_params.disk_size_gb:
            logger.debug("Boot disk size is different, updating boot disk size")
            disk.initialize_params.disk_size_gb = new_disks[i].initialize_params.disk_size_gb
        if disk.initialize_params.disk_type != new_disks[i].initialize_params.disk_type:
            logger.debug("Boot disk type is different, updating boot disk type") 
            disk.initialize_params.disk_type = new_disks[i].initialize_params.disk_type
    # check the machine type
    if template.properties.machine_type != machine_type:
        logger.debug("Machine type is different, updating machine type")
        template.properties.machine_type = machine_type

    # check the startup script url
    if template.properties.metadata.items[0].value != startup_script_url:
        logger.debug("Startup script url is different, updating startup script url")
        template.properties.metadata.items[0].value = startup_script_url

    # check the shutdown script url
    if template.properties.metadata.items[1].value != shutdown_script_url:
        logger.debug("Shutdown script url is different, updating shutdown script url")
        template.properties.metadata.items[1].value = shutdown_script_url

    # setting labels
    template.properties.labels  = labels

    # send the update request


    # create the new template
    operation = template_client.insert(
        project=project_id, instance_template_resource=template
    )

    wait_for_extended_operation(operation, "instance template update") 
    logger.success("Instance template updated!")

    
    return template_client.get(project=project_id, instance_template=template.name)
    


def __get_instance_template(
    template_client,
    project_id: str, template_name: str
) -> compute_v1.InstanceTemplate:
    """
    Retrieve an instance template, which you can use to create virtual machine
    (VM) instances and managed instance groups (MIGs).
    Args:
        project_id: project ID or project number of the Cloud project you use.
        template_name: name of the template to retrieve.
    Returns:
        InstanceTemplate object that represents the retrieved template.
    """
    logger.info("Retrieving instance template...")
    # try to get template by name if an exception of 404 
    # if thrown then return None
    try:
        return template_client.get(project=project_id, instance_template=template_name)
    except Exception as e:
        logger.error("Instance template not found")
        logger.error(e)
        return None


def __list_instance_templates(template_client, project_id: str) -> Iterable[compute_v1.InstanceTemplate]:
    """
    Get a list of InstanceTemplate objects available in a project.
    Args:
        project_id: project ID or project number of the Cloud project you use.
    Returns:
        Iterable list of InstanceTemplate objects.
    """
    return template_client.list(project=project_id)


def __delete_instance_template(template_client, project_id: str, template_name: str):
    """
    Delete an instance template.
    Args:
        project_id: project ID or project number of the Cloud project you use.
        template_name: name of the template to delete.
    """
    operation = template_client.delete(
        project=project_id, instance_template=template_name
    )
    wait_for_extended_operation(operation, "instance template deletion")
    return


def __delete_all_templates(template_client, project_id):
    """
    Delete all instance templates in a project.
    Args:
        project_id: project ID or project number of the Cloud project you use.
    """
    for template in list_instance_templates(template_client, project_id):
        delete_instance_template(template_client, project_id, template.name)
    print("All templates are deleted.")

