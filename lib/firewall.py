import sys
from typing import Any

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1

from utils.gcp import wait_for_extended_operation




# TODO this can be updated with specific values  
# Create a firewall rule 
def create_firewall_rule(
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

    firewall_client = compute_v1.FirewallsClient()
    operation = firewall_client.insert(
        project=project_id, firewall_resource=firewall_rule
    )

    wait_for_extended_operation(operation, "firewall rule creation")


# Check if the firewall rule exists 
def check_firewall_rule(project_id: str, firewall_rule_name: str) -> bool:
    # create a firewall client
    firewall_client = compute_v1.FirewallsClient()

    # check if the firewall rule exists
    try:
        firewall_client.get(project=project_id, firewall=firewall_rule_name)
        return True
    except Exception as e:
        return False




















