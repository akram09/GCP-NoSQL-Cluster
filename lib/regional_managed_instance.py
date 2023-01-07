import time 
from lib.template import get_instance_template
from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation, get_image_from_family

# create managed instance group 
def create_region_managed_instance_group(project_id, region, instance_group_name, instance_template_name, instance_group_size):
    # get instance template 
    instance_template = get_instance_template(project_id, instance_template_name)
    # create instance group manager client
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    # create instance group manager request
    instance_group_manager_request = create_region_managed_instance_group_request(project_id, region, instance_group_name, instance_template, instance_group_size)
    # create instance group manager
    operation = instance_group_manager_client.insert(
        request=instance_group_manager_request
    )
    # wait for operation to complete
    wait_for_extended_operation(operation, "instance group manager creation")
    # get instance group manager
    instance_group_manager = instance_group_manager_client.get(
        project=project_id, region=region, instance_group_manager=instance_group_name
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
    
    # wait till the instance group manager is stable 
    while not instance_group_manager.status.is_stable:
        print("Waiting for instance group manager to be stable")
        time.sleep(5)
        instance_group_manager = instance_group_manager_client.get(
            project=project_id, region=region, instance_group_manager=instance_group_name
        )
    print("Instance group manager is stable")
    # witing for instances to be provisioned
    print("Waiting for instances to be provisioned")
    time.sleep(60)
    # return instance group manager
    return instance_group_manager



# list instances of an instance group manager
def list_region_instances(project_id, region, instance_group_name):
    # create instance group manager client
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    # create instance group manager request
    instance_group_manager_request = compute_v1.ListManagedInstancesRegionInstanceGroupManagersRequest(
        project=project_id, region=region, instance_group_manager=instance_group_name
    )
    # list instances
    instances = instance_group_manager_client.list_managed_instances(
        request=instance_group_manager_request
    )
    # return list 
    return instances


# create managed instance group request 
def create_region_managed_instance_group_request(project_id, region, instance_group_name, instance_template, target_size):
    """
    Creates a request to create a managed instance group.
    Args:
        project_id: ID or number of the project you want to use.
        region: Region where the managed instance group will be created.
        instance_group_name: Name of the managed instance group.
        instance_template: Template used for creating the managed instance group.
        target_size: Target size of the managed instance group.
    Returns:
        RegionInsertInstanceGroupManagerRequest
    """
    # create instance group manager request
    instance_group_manager_request = compute_v1.InsertRegionInstanceGroupManagerRequest()
    # set project id
    instance_group_manager_request.project = project_id
    # set region
    instance_group_manager_request.region = region
    # create distribution policy
    distribution_policy = compute_v1.DistributionPolicy()
    
    # set target shape 
    print(f"target shape of distribution policy: ANY'")
    print("When the target shape is ANY, the group manager will create instances across all available zones that respect the resource constraints.")
    distribution_policy.target_shape = "BALANCED"

    instance_group_manager_request.instance_group_manager_resource = compute_v1.InstanceGroupManager(
        name=instance_group_name,
        base_instance_name=instance_group_name,
        instance_template=instance_template.self_link,
        target_size=target_size,
        # add stateful policy to instance group manager
        stateful_policy=compute_v1.StatefulPolicy(
            preserved_state=compute_v1.StatefulPolicyPreservedState(
                disks=
                    {
                        "persistent-disk-0" : 
                            compute_v1.StatefulPolicyPreservedStateDiskDevice(
                                auto_delete="never"
                            )
                    }
            )
        ),
        # set distribution policy to the MIG 
        distribution_policy=distribution_policy,
        # set update policy 
        update_policy=compute_v1.InstanceGroupManagerUpdatePolicy(
            instance_redistribution_type="NONE",
        ),

        # add autohealing policy to instance group manager
        # auto_healing_policies=[
        #     compute_v1.InstanceGroupManagerAutoHealingPolicy(
        #         health_check=health_check['self_link'],
        #         initial_delay_sec=60,
        #     )
        # ],
    )

    return instance_group_manager_request    
