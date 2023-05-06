# Description: This file contains the functions to create, update and delete a managed instance group
from shared.lib.template import get_instance_template
from shared.lib.regional_managed_instance import update_region_managed_instance_group, create_region_managed_instance_group, get_region_managed_instance_group, delete_region_managed_instance_group, region_adding_instances, region_scaling_mig
from loguru import logger
from utils.exceptions import GCPInstanceTemplateAlreadyExistsException, GCPInstanceTemplateNotFoundException, GCPManagedInstanceGroupNotFoundException, GCPManagedInstanceGroupAlreadyExistsException


def create_managed_instance_group(gcp_project, managed_instance_group_params):
    """
    Create a managed instance group. It checks if the instance template exists and if the managed instance group already exists.
    """
    # check if the instance template exists
    instance_template = get_instance_template(gcp_project, managed_instance_group_params['instance_template'])
    if not instance_template:
        raise GCPInstanceTemplateNotFoundException(f"Instance template {managed_instance_group_params['instance_template']} not found")
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if managed_instance_group:
        raise GCPManagedInstanceGroupAlreadyExistsException(f"Managed instance group {managed_instance_group_params['name']} already exists")
    # create the managed instance group
    logger.info(f"Creating managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = create_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'], instance_template) 
    region_adding_instances(gcp_project, managed_instance_group_params['region'], managed_instance_group, managed_instance_group_params['size'])
    return managed_instance_group


def update_managed_instance_group(gcp_project, managed_instance_group_params):
    """
    Update a managed instance group. It checks if the instance template exists and if the managed instance group already exists.
    """
    # check if the instance template exists
    instance_template = get_instance_template(gcp_project, managed_instance_group_params['instance_template'])
    if not instance_template:
        raise GCPInstanceTemplateNotFoundException(f"Instance template {managed_instance_group_params['instance_template']} not found")
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if not managed_instance_group:
        raise GCPManagedInstanceGroupNotFoundException(f"Managed instance group {managed_instance_group_params['name']} not found")
    # update the managed instance group
    logger.info(f"Updating managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = update_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'], instance_template)
    region_scaling_mig(gcp_project, managed_instance_group_params['region'], managed_instance_group, managed_instance_group.target_size, managed_instance_group_params['size'])
    return managed_instance_group


def delete_managed_instance_group(gcp_project, managed_instance_group_params):
    """
    Delete a managed instance group. It checks if the managed instance group already exists.
    Raises an exception if the managed instance group does not exist.
    """
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if not managed_instance_group:
        raise GCPManagedInstanceGroupNotFoundException(f"Managed instance group {managed_instance_group_params['name']} not found")
    # delete the managed instance group
    logger.info(f"Deleting managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = delete_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    return managed_instance_group
