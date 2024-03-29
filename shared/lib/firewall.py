# Description: This file contains the functions to create a firewall rule for the couchbase servers.
import sys
from loguru import logger
from typing import Any
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
import google.oauth2.credentials
from utils.shared import wait_for_extended_operation




def setup_firewall(project, cluster_name):
    """
    Creates a firewall rule to allow the couchbase servers to communicate with each other.
    """
    # create client 
    client = create_firewalls_client(project)

    # Check if the firewall rule exists
    if __check_firewall_rule(client, project.project_id, cluster_name+"-firewall"):
        logger.debug(f"Firewall rule {cluster_name}-firewall already exists")
    else:
        logger.debug(f"Creating firewall rule {cluster_name}-firewall")
        __create_firewall_rule(client, project.project_id, cluster_name+"-firewall")
        logger.success(f"Firewall rule {cluster_name}-firewall created")







# public function
def create_firewall_rule(project, firewall_rule_name: str, network: str = "global/networks/default"):
    client = create_firewalls_client(project)
    return __create_firewall_rule(client, project.project_id, firewall_rule_name, network)


# public function
def check_firewall_rule_exists(project, firewall_rule_name: str):
    client = create_firewalls_client(project)
    return __check_firewall_rule_exists(client, project.project_id, firewall_rule_name)



# create firewalls client
def create_firewalls_client(project):
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return compute_v1.FirewallsClient(credentials=credentials)
    # create the firewalls client
    return compute_v1.FirewallsClient()


# private function to create a firewall rule
def __create_firewall_rule(
    firewall_client, 
    project_id: str, firewall_rule_name: str, network: str = "global/networks/default"
):
    """
    Creates a new firewall rule to allow the couchbase servers to communicate with each other.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        firewall_rule_name: name of the rule that is created.
        network: name of the network the rule will be applied to. Available name formats:
    """
    firewall_rule = compute_v1.Firewall()
    firewall_rule.name = firewall_rule_name
    firewall_rule.direction = "INGRESS"

    allowed_ports = compute_v1.Allowed()
    allowed_ports.I_p_protocol = "tcp"
    allowed_ports.ports = ["8091"]

    firewall_rule.allowed = [allowed_ports]
    firewall_rule.source_ranges = ["0.0.0.0/0"]
    firewall_rule.network = network
    firewall_rule.description = "Allowing TCP traffic on port 80 and 443 from Internet."

    firewall_rule.target_tags = ["couchbase-server"]

    # TODO: Uncomment to set the priority to 0
    # firewall_rule.priority = 0

    operation = firewall_client.insert(
        project=project_id, firewall_resource=firewall_rule
    )

    wait_for_extended_operation(operation, "firewall rule creation")


# private function to check if the firewall rule exists
def __check_firewall_rule(firewall_client, project_id: str, firewall_rule_name: str) -> bool:

    # check if the firewall rule exists
    try:
        firewall_client.get(project=project_id, firewall=firewall_rule_name)
        return True
    except Exception as e:
        return False

