from loguru import logger
import time 
from lib.template import get_instance_template
from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation, get_image_from_family

# create managed instance group 
def create_region_managed_instance_group(project_id, region, instance_group_name, instance_template_name):
    logger.info(f"Creating managed instance group {instance_group_name} with zero instances")
    # get instance template 
    instance_template = get_instance_template(project_id, instance_template_name)
    # create instance group manager client
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    # create instance group manager request
    instance_group_manager_request = create_region_managed_instance_group_request(project_id, region, instance_group_name, instance_template, 0)
    # create instance group manager
    operation = instance_group_manager_client.insert(
        request=instance_group_manager_request
    )
    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project_id)
    except Exception as e:
        logger.error(f"Error creating managed instance group: {e}")
        raise e
    logger.success(f"Managed instance group {instance_group_name} created")

    # get instance group manager
    instance_group_manager = instance_group_manager_client.get(
        project=project_id, region=region, instance_group_manager=instance_group_name
    )    
    # wait till the instance group manager is stable 
    while not instance_group_manager.status.is_stable:
        logger.debug(f"Waiting for instance group manager {instance_group_name} to be stable")
        time.sleep(5)
        instance_group_manager = instance_group_manager_client.get(
            project=project_id, region=region, instance_group_manager=instance_group_name
        )
    logger.debug(f"Instance group manager {instance_group_name} is stable")
    # return instance group manager
    return instance_group_manager


def get_region_managed_instance_group(project_id, region, instance_group_name):
    logger.info("Checking if the managed instance group exists ...")
    # create instance group manager client
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    # get instance group manager
    try:
        instance_group_manager = instance_group_manager_client.get(
            project=project_id, region=region, instance_group_manager=instance_group_name
        )
        logger.debug("Managed instance group exists")
        return instance_group_manager
    except Exception as e:
        logger.debug("Managed instance group does not exist")
        return None


# adding custom instances to the managed instance group 
def region_adding_instances(
    project_id, region, instance_group_manager, size
    ):
    logger.debug(f"Adding {size} instances to the managed instance group {instance_group_manager.name}")
    # get client 
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    # create an instance group managers create instance request
    create_instance_request = compute_v1.CreateInstancesRegionInstanceGroupManagerRequest(
        project=project_id,
        region=region,
        instance_group_manager=instance_group_manager.name,
        region_instance_group_managers_create_instances_request_resource={
            "instances": [
                {
                    # format the name to 3 digits 
                    "name": f"{instance_group_manager.name}-{instance_range:03d}"
                }
                for instance_range in range(size)
            ]
        },
    )
    # create instances 
    operation = instance_group_manager_client.create_instances(
        request=create_instance_request
    )
    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project_id)
    except Exception as e:
        logger.error(f"Error creating instances: {e}")
        raise e
    logger.success(f"Instances created")

    

# scaling up the mig or down
def region_scaling_mig(
    project_id, region, instance_group_manager, size, wanted_size
    ):
    logger.debug(f"Scaling managed instance group {instance_group_manager.name} from {size} to {wanted_size} instances")
    # get client 
    instance_group_manager_client = compute_v1.RegionInstanceGroupManagersClient()
    if size < wanted_size: 
        # create an instance group managers create instance request
        create_instance_request = compute_v1.CreateInstancesRegionInstanceGroupManagerRequest(
            project=project_id,
            region=region,
            instance_group_manager=instance_group_manager.name,
            region_instance_group_managers_create_instances_request_resource={
                "instances": [
                    {
                        # format the name to 3 digits 
                        "name": f"{instance_group_manager.name}-{instance_range:03d}"
                    }
                    for instance_range in range(size, wanted_size)
                ]
            },
        )
        # create instances 
        operation = instance_group_manager_client.create_instances(
            request=create_instance_request
        )
        # wait for operation to complete
        try:
            wait_for_extended_operation(operation, project_id)
        except Exception as e:
            logger.error(f"Error scaling instances: {e}")
            raise e
        logger.success(f"Instances scaled")
    elif size > wanted_size:
        # list all the instances to get the zone of the instances to delete 
        managed_instances =  list_region_instances(project_id, region, instance_group_manager.name)
        instances_zones = [ {"name": managed_instance.instance, "index": int(managed_instance.instance.split('/')[-1].split('-')[-1]) } for managed_instance in managed_instances]
        # sort the instances by index
        instances_zones.sort(key=lambda x: x['index'])
        # get the instances to delete
        instances_to_delete = instances_zones[-(size - wanted_size):]
        # removing some instances 
        delete_instance_request = compute_v1.DeleteInstancesRegionInstanceGroupManagerRequest(
            project=project_id,
            region=region,
            instance_group_manager=instance_group_manager.name,
            region_instance_group_managers_delete_instances_request_resource={
                "instances": [
                    # full url
                    instances_to_delete[i]['name']
                    for i in range(len(instances_to_delete))
                ]
            },
        )
        print(delete_instance_request)
        # delete instances
        operation = instance_group_manager_client.delete_instances(
            request=delete_instance_request
        )
        # wait for operation to complete
        try:
            wait_for_extended_operation(operation, project_id)
        except Exception as e:
            logger.error(f"Error scaling instances: {e}")
            raise e
        logger.success(f"Instances scaled")


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
                            ),
                        "persistent-disk-1" : 
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
            type="OPPORTUNISTIC",
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
