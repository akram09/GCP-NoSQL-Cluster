from loguru import logger
import time 
from google.cloud import compute_v1
from utils.shared import wait_for_extended_operation
import google.oauth2.credentials
from utils.exceptions import GCPInstanceSerialOutputException




# public function
def get_instance_serial_output(project, zone, instance_name):
    # create client 
    client = create_intances_client(project)

    # get the serial output
    return __get_instance_serial_output(client, project.project_id, zone, instance_name)




def create_intances_client(project):
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return compute_v1.InstancesClient(credentials=credentials)
    # create the firewalls client
    return compute_v1.InstancesClient()





# private function 
def __get_instance_serial_output(
    instance_client, project_id: str, zone: str, instance_name: str
) -> str:
    """
    Get the serial port output from a running instance.
    Args:
        instance_client: InstanceClient object.
        project_id: project ID or project number of the Cloud project you want to get instance from.
        zone: name of the zone you want to get instance from.
        instance_name: name of the instance you want to get serial port output from.
    Returns:
        A string of the serial port output.
    """
    logger.info(f"Getting serial port output from instance {instance_name}")
    try:
        output = instance_client.get_serial_port_output(
            project=project_id, zone=zone, instance=instance_name
        )
        return output.contents
    except Exception as e:
        logger.error(f"Error getting serial port output from instance {instance_name}: {e}")
        raise GCPInstanceSerialOutputException(f"Error getting serial port output from instance {instance_name}: {e}")
