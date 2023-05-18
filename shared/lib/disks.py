# Description: This file contains functions that create disks to be used in VM instance creation.
from google.cloud import kms_v1
from google.cloud import compute_v1
from shared.lib.instances import create_intances_client
from loguru import logger
from utils.shared import wait_for_extended_operation
import google.oauth2.credentials
from google.cloud import compute_v1





def create_disk(project, zone, disk_name, disk_type, disk_size_gb, source_image):
    client = create_disks_client(project)
    return __create_disk(client, project, zone, disk_name, disk_type, disk_size_gb, source_image)

# create disks client 

def create_disks_client(project): 
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return compute_v1.DisksClient(credentials=credentials)
    # create the instance templates client
    return compute_v1.DisksClient()





def __create_disk(
    client,
    project,
    zone,
    disk_name,
    disk_type,
    disk_size_gb,
    source_image,
    ) -> compute_v1.Disk:
        """
        Create a disk object to be used in VM instance creation. Uses an image as the source for the new disk.

        """
        # create the disk object
        disk = compute_v1.Disk()
        # set the disk type
        disk_type_url = f"projects/{project.project_id}/zones/{zone}/diskTypes/{disk_type}"
        disk.type = disk_type_url
        # set the disk size
        disk.size_gb = disk_size_gb
        # set the source image
        disk.source_image = source_image
        # set the disk name
        disk.name = disk_name
        # insert the disk 
        operation = client.insert(
            project=project.project_id,
            zone=zone,
            disk_resource=disk,
        )

        # wait for operation to complete
        try:
            wait_for_extended_operation(operation, project.project_id)
        except Exception as e:
            logger.error(f"Error creating disk {disk_name} in project {project.project_id}")
            raise e

        # get the disk url 
        disk_url = f"projects/{project.project_id}/zones/{zone}/disks/{disk.name}"
        logger.success(f"Disk {disk.name} created in project {project.project_id} and zone {zone}")
        return disk_url
        





def disk_from_image(
    disk_type,
    disk_size_gb,
    disk_enc_dec_key,
    boot,
    source_image,
    auto_delete,
) -> compute_v1.AttachedDisk:
    """
    Create an AttachedDisk object to be used in VM instance creation. Uses an image as the
    source for the new disk.
    Args:
         disk_type: the type of disk you want to create. This value uses the following format:
            "zones/{zone}/diskTypes/(pd-standard|pd-ssd|pd-balanced|pd-extreme)".
            For example: "zones/us-west3-b/diskTypes/pd-ssd"
        disk_size_gb: size of the new disk in gigabytes
        disk_enc_dec_key: KMS symmectric key used to encrypt/decrypt the disk
        boot: boolean flag indicating whether this disk should be used as a boot disk of an instance
        source_image: source image to use when creating this disk. You must have read access to this disk. This can be one
            of the publicly available images or an image from one of your projects.
            This value uses the following format: "projects/{project_name}/global/images/{image_name}"
        auto_delete: boolean flag indicating whether this disk should be deleted with the VM that uses it
    Returns:
        AttachedDisk object configured to be created using the specified image.
    """
    boot_disk = compute_v1.AttachedDisk()
    
    if disk_enc_dec_key:
        # check if encryption key is dict 
        if isinstance(disk_enc_dec_key, dict):
            key_name = disk_enc_dec_key.get("name")
        else:
            key_name = disk_enc_dec_key.name

    # Set the encryption key on the boot disk
    if disk_enc_dec_key:
        disk_encryption_key = compute_v1.CustomerEncryptionKey(
            kms_key_name=key_name
        )
        boot_disk.disk_encryption_key = disk_encryption_key

    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = source_image
    initialize_params.disk_size_gb = disk_size_gb
    initialize_params.disk_type = disk_type
    boot_disk.initialize_params = initialize_params
    # Remember to set auto_delete to True if you want the disk to be deleted when you delete
    # your VM instance.
    boot_disk.auto_delete = auto_delete
    boot_disk.boot = boot
    return boot_disk


def attach_disk(
    project,
    zone: str,
    instance_name: str,
    disk
) :
    """
    Attach a disk to an instance
    """
    compute_client = create_intances_client(project)

    # Add the disk to the instance 
    logger.info(f"Attaching disk {instance_name} to instance {instance_name} in project {project.project_id} and zone {zone}")

    attached_disk = compute_v1.AttachedDisk()
    attached_disk.source = disk

    operation = compute_client.attach_disk(
            project=project.project_id,
            zone=zone,
            instance=instance_name,
            attached_disk_resource=attached_disk,
            )
    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project.project_id)
    except Exception as e:
        logger.error(f"Error creating disk {instance_name} in project {project.project_id} and zone {zone}")
        raise e
    logger.success(f"Disk {instance_name} created in project {project.project_id} and zone {zone}")



