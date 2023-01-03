from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation, disk_from_image
from typing import Iterable

def create_template(
    project_id: str,
    zone: str,
    template_name: str,
    machine_type: str,
    machine_image: compute_v1.types.compute.Image,
    disk_type: str,
    disk_size: int,
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
    # get disk from image
    #disk_type_name = f"zones/{zone}/diskTypes/{disk_type}"
    disk = disk_from_image(disk_type, disk_size, disk_boot_auto, machine_image.self_link)
    # initialize_params = compute_v1.AttachedDiskInitializeParams()
    # initialize_params.source_image = (
    #     machine_image
    # )
    # initialize_params.disk_size_gb = 250
    # disk.initialize_params = initialize_params
    # disk.auto_delete = True
    # disk.boot = True

    # The template connects the instance to the `default` network,
    # without specifying a subnetwork.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"

    # The template lets the instance use an external IP address.
    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type_ = "ONE_TO_ONE_NAT"
    access_config.network_tier = "PREMIUM"
    network_interface.access_configs = [access_config]

    template = compute_v1.InstanceTemplate()
    template.name = template_name
    template.properties.disks = [disk]
    template.properties.machine_type = machine_type
    template.properties.network_interfaces = [network_interface]

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