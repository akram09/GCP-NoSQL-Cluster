# Description: This file contains the functions to create, update and delete instance templates
from shared.lib.kms import setup_encryption_keys
from shared.lib.template import create_template, get_instance_template, update_template, delete_template
from loguru import logger
from utils.exceptions import GCPInstanceTemplateAlreadyExistsException, GCPInstanceTemplateNotFoundException
from shared.lib.images import get_image_from_family


def create_instance_template(gcp_project, instance_template_params):
    """
    Create an instance template with the given parameters.
    """
    # checking encyrption keys 
    logger.info(f"Checking encryption keys ....")
    encryption_key = setup_encryption_keys(gcp_project, instance_template_params.name, instance_template_params.region)
   
    # creating instance template
    #Get the machine image from the project and family
    machine_image = get_image_from_family(gcp_project, instance_template_params.image_project, instance_template_params.image_family)
    
    template = get_instance_template(gcp_project, instance_template_params.name)
    # check if there is a template existing 
    if template is None: 
        logger.info(f"Instance template does not exist, creating ...")
        # create instance template
        template = create_template(
            gcp_project,
            instance_template_params.name, 
            instance_template_params.machine_type,
            machine_image,
            instance_template_params.disks,
            encryption_key,
            instance_template_params.startup_script_url,
            instance_template_params.shutdown_script_url,
            instance_template_params.labels 
        )
    else:
        logger.debug(f"Instance template {instance_template_params.name}  already exists")
        raise GCPInstanceTemplateAlreadyExistsException(f"Instance template {instance_template_params.name} already exists")

def update_instance_template(gcp_project, instance_template_params):
    """
    Update an instance template with the given parameters.
    """
    # checking encyrption keys 
    logger.info(f"Checking encryption keys ....")
    encryption_key = setup_encryption_keys(gcp_project, instance_template_params.name, instance_template_params.region)
   
    #Get the machine image from the project and family
    machine_image = get_image_from_family(gcp_project, instance_template_params.image_project, instance_template_params.image_family)
    
    template = get_instance_template(gcp_project, instance_template_params.name)
    # check if there is a template existing 
    if template is None: 
        logger.info(f"Instance template does not exist")
        raise GCPInstanceTemplateNotFoundException(f"Instance template {instance_template_params.name} does not exist")
    else:
        logger.debug(f"Instance template {instance_template_params.name} found ")
        # update instance instance_template_params
        template = update_template(
            gcp_project,
            template,
            instance_template_params.machine_type,
            machine_image,
            instance_template_params.disks,
            encryption_key,
            instance_template_params.startup_script_url,
            instance_template_params.shutdown_script_url,
            instance_template_params.labels 
        )
def delete_instance_template(gcp_project, instance_template_name):
    """
    Delete an instance template with the given parameters.
    """
    logger.info(f"Deleting instance template {instance_template_name} ...")
    template = get_instance_template(gcp_project, instance_template_name)
    # check if there is a template existing
    if template is None:
        logger.info(f"Instance template {instance_template_name} does not exist")
        raise GCPInstanceTemplateNotFoundException(f"Instance template {instance_template_name} does not exist")
    else:
        logger.debug(f"Instance template {instance_template_name} found ")
        # delete instance template
        delete_template(gcp_project, instance_template_name)
