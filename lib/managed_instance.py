from lib.template import get_instance_template
from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation

# create managed instance group 
def create_managed_instance_group(project_id, zone, instance_group_name, instance_template_name):
    # get instance template 
    instance_template = get_instance_template(project_id, instance_template_name)
    # create instance group manager client
    instance_group_manager_client = compute_v1.InstanceGroupManagersClient()
    # create instance group manager request
    instance_group_manager_request = create_managed_instance_group_request(project_id, zone, instance_group_name, instance_template, 2)
    # create instance group manager
    operation = instance_group_manager_client.insert(
        request=instance_group_manager_request
    )
    # wait for operation to complete
    wait_for_extended_operation(operation, "instance group manager creation")
    # get instance group manager
    instance_group_manager = instance_group_manager_client.get(
        project=project_id, zone=zone, instance_group_manager=instance_group_name
    )
    # print instance group manager details
    print(f"Instance group manager {instance_group_name} created.")
    print(f"Instance template: {instance_template.name}")
    print(f"Instance template self link: {instance_template.self_link}")
    print(f"Instance group manager self link: {instance_group_manager.self_link}")
    print(f"Instance group manager target size: {instance_group_manager.target_size}")
    print(f"Instance group manager instance template: {instance_group_manager.instance_template}")
    print(f"Instance group manager base instance name: {instance_group_manager.base_instance_name}")
    print(f"Instance group manager status: {instance_group_manager.status}")

# create managed instance group request 
def create_managed_instance_group_request(project_id, zone, instance_group_name, instance_template, target_size):
    """
    Creates a request to create a managed instance group.
    Args:
        project_id: ID or number of the project you want to use.
        zone: Name of the zone you want to check, for example: us-west3-b
        instance_group_name: Name of the managed instance group.
        instance_template: Template used for creating the managed instance group.
        target_size: Target size of the managed instance group.
    Returns:
        InsertInstanceGroupManagerRequest object.
    """
    # create instance group manager request
    instance_group_manager_request = compute_v1.InsertInstanceGroupManagerRequest()
    # set project id
    instance_group_manager_request.project = project_id
    # set zone
    instance_group_manager_request.zone = zone
    # set instance group manager resource
    instance_group_manager_request.instance_group_manager_resource = compute_v1.InstanceGroupManager(
        name=instance_group_name,
        base_instance_name=instance_group_name,
        instance_template=instance_template.self_link,
        target_size=target_size,
    )
    # return instance group manager request
    return instance_group_manager_request
    
