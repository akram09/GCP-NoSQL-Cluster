from shared.lib.disks import disk_from_image, attach_disk, create_disk
from shared.lib.images import get_image_from_family
from loguru import logger

def attach_disk_to_instance(
        project,
        zone: str,
        disk_name: str,
        instance_name: str,
        disk_type,
        disk_size_gb,
        image_family,
        image_project,
        auto_delete,
        ):
    """
    Attach a disk to an instance
    """
    # get image 
    image = get_image_from_family(project, image_project, image_family)

    
    # create disk
    disk = create_disk(project, zone, disk_name, disk_type, disk_size_gb, image.self_link)

    logger.info(f"Attaching disk {disk_name} to instance {instance_name} in project {project.project_id} and zone {zone} ") 
    # attach disk to instance
    attach_disk(
        project,
        zone,
        instance_name,
        disk
    )
    logger.success(f"Disk {instance_name} created in project {project.project_id} and zone {zone}")


