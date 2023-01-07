from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation, disk_from_image
from typing import Iterable
from lib.kms import create_key_ring, create_key_symmetric_encrypt_decrypt
import os

def create_template(
    project_id: str,
    zone: str,
    template_name: str,
    machine_type: str,
    machine_image: compute_v1.types.compute.Image,
    disk_type: str,
    disk_size: int,
    startup_script_url: str,
    disk_boot_auto: bool = True
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


    # Create KMS key ring and symmetric encryption/decryption key
    key_ring_id = f"key-ring-{template_name.replace('template-', '')}"
    key_ring = create_key_ring(project_id, "global", key_ring_id)
    key_id = f"key-{template_name.replace('template-', '')}"
    key = create_key_symmetric_encrypt_decrypt(project_id, "global", key_ring_id, key_id) 
    
    # get disk from image
    disk = disk_from_image(disk_type, disk_size, key, disk_boot_auto, machine_image.self_link)
    # Add google API support in the template so that it can be used inside the vm


    # The template connects the instance to the `default` network,
    # without specifying a subnetwork.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"

    template = compute_v1.InstanceTemplate()
    template.name = template_name
    # create instance tags 
    tags = compute_v1.Tags()
    tags.items = ["couchbase-server"]
    template.properties.tags = tags 
    template.properties.disks = [disk]
    template.properties.machine_type = machine_type
    template.properties.network_interfaces = [network_interface]

    # get email from COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL environment variable
    email = os.environ["COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL"]
    #set scopes in serviceaccounts
    service_account = compute_v1.ServiceAccount()
    service_account.email = email
    service_account.scopes = [
        "https://www.googleapis.com/auth/devstorage.read_only",
    ]
    template.properties.service_accounts = [service_account]
    print(service_account)
    # set the startup script url in the metadata
    metadata = compute_v1.Metadata()
    metadata.items = [
        {
            "key": "startup-script-url",
            "value": startup_script_url
        }
    ]
    template.properties.metadata = metadata


    template_client = compute_v1.InstanceTemplatesClient()
    operation = template_client.insert(
        project=project_id, instance_template_resource=template
    )

    wait_for_extended_operation(operation, "instance template creation")

    return template_client.get(project=project_id, instance_template=template_name)


def get_instance_template(
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
    template_client = compute_v1.InstanceTemplatesClient()
    return template_client.get(project=project_id, instance_template=template_name)


def list_instance_templates(project_id: str) -> Iterable[compute_v1.InstanceTemplate]:
    """
    Get a list of InstanceTemplate objects available in a project.
    Args:
        project_id: project ID or project number of the Cloud project you use.
    Returns:
        Iterable list of InstanceTemplate objects.
    """
    template_client = compute_v1.InstanceTemplatesClient()
    return template_client.list(project=project_id)


def delete_instance_template(project_id: str, template_name: str):
    """
    Delete an instance template.
    Args:
        project_id: project ID or project number of the Cloud project you use.
        template_name: name of the template to delete.
    """
    template_client = compute_v1.InstanceTemplatesClient()
    operation = template_client.delete(
        project=project_id, instance_template=template_name
    )
    wait_for_extended_operation(operation, "instance template deletion")
    return


def delete_all_templates(project_id):
    """
    Delete all instance templates in a project.
    Args:
        project_id: project ID or project number of the Cloud project you use.
    """
    for template in list_instance_templates(project_id):
        delete_instance_template(project_id, template.name)
    print("All templates are deleted.")

