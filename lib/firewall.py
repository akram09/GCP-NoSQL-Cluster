import sys
from typing import Any
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
import google.oauth2.credentials
from utils.gcp import wait_for_extended_operation


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


# Create a firewall rule 
def create_firewall_rule(
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


# Check if the firewall rule exists 
def check_firewall_rule(firewall_client, project_id: str, firewall_rule_name: str) -> bool:

    # check if the firewall rule exists
    try:
        firewall_client.get(project=project_id, firewall=firewall_rule_name)
        return True
    except Exception as e:
        return False




















