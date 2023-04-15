from shared.lib.template import get_instance_template
from shared.lib.regional_managed_instance_group import update_region_managed_instance_group, create_region_managed_instance_group, get_region_managed_instance_group, delete_region_managed_instance_group
from loguru import logger
from utils.exceptions import GCPInstanceTemplateAlreadyExistsException, GCPInstanceTemplateNotFoundException, ManagedInstanceGroupAlreadyExistsException, ManagedInstanceGroupNotFoundException


def create_managed_instance_group(gcp_project, managed_instance_group_params):
    # check if the instance template exists
    instance_template = get_instance_template(gcp_project, managed_instance_group_params['instance_template'])
    if not instance_template:
        raise GCPInstanceTemplateNotFoundException(f"Instance template {managed_instance_group_params['instance_template']} not found")
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if managed_instance_group:
        raise ManagedInstanceGroupAlreadyExistsException(f"Managed instance group {managed_instance_group_params['name']} already exists")
    # create the managed instance group
    logger.info(f"Creating managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = create_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'], managed_instance_group_params['instance_template'])
    return managed_instance_group


def update_managed_instance_group(gcp_project, managed_instance_group_params):
    # check if the instance template exists
    instance_template = get_instance_template(gcp_project, managed_instance_group_params['instance_template'])
    if not instance_template:
        raise GCPInstanceTemplateNotFoundException(f"Instance template {managed_instance_group_params['instance_template']} not found")
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if not managed_instance_group:
        raise ManagedInstanceGroupNotFoundException(f"Managed instance group {managed_instance_group_params['name']} not found")
    # update the managed instance group
    logger.info(f"Updating managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = update_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'], managed_instance_group_params['instance_template'])
    return managed_instance_group


def delete_managed_instance_group(gcp_project, managed_instance_group_params):
    # check if the managed instance group already exists
    managed_instance_group = get_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    if not managed_instance_group:
        raise ManagedInstanceGroupNotFoundException(f"Managed instance group {managed_instance_group_params['name']} not found")
    # delete the managed instance group
    logger.info(f"Deleting managed instance group {managed_instance_group_params['name']} ...")
    managed_instance_group = delete_region_managed_instance_group(gcp_project, managed_instance_group_params['region'], managed_instance_group_params['name'])
    return managed_instance_group
