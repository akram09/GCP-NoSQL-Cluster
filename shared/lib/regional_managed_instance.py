# Description: This file contains functions to create, update, delete, and list regional managed instance groups
from loguru import logger
import re
import time 
from shared.lib.template import get_instance_template
from shared.lib.instances import get_instance_serial_output
from google.cloud import compute_v1
from utils.shared import wait_for_extended_operation
import google.oauth2.credentials



# public function 
def apply_updates_to_instances(project, region, instance_group_manager):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # apply updates to instances
    return __apply_updates_to_instances(instance_group_manager_client, project, region, instance_group_manager)




# public function 
def update_region_managed_instance_group(project, region, instance_group_name, instance_template):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # update the managed instance group
    return __update_region_managed_instance_group(instance_group_manager_client, project.project_id, region, instance_group_name, instance_template)


# public function 
def create_region_managed_instance_group(project, region, instance_group_name, instance_template):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # create the managed instance group
    return __create_region_managed_instance_group(instance_group_manager_client, project.project_id, region, instance_group_name, instance_template)

# public function 
def get_region_managed_instance_group(project, region, instance_group_name):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # get the managed instance group
    return __get_region_managed_instance_group(instance_group_manager_client, project.project_id, region, instance_group_name)

# public function 
def region_adding_instances(project, region, instance_group_name, instance_template):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # add instances to the managed instance group
    return __region_adding_instances(instance_group_manager_client, project.project_id, region, instance_group_name, instance_template)

# public function 
def region_scaling_mig(project, region, instance_group_name, instance_template, target_size):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # scale the managed instance group
    return __region_scaling_mig(instance_group_manager_client, project.project_id, region, instance_group_name, instance_template, target_size)


# public function 
def list_region_instances(project, region, instance_group_name):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # list the instances in the managed instance group
    return __list_region_instances(instance_group_manager_client, project.project_id, region, instance_group_name)

# public function
# delete the managed instance group 
def delete_region_managed_instance_group(project, region, instance_group_name):
    # create the instance group managers client
    instance_group_manager_client = create_region_instance_group_managers_client(project)
    # delete the managed instance group
    return __delete_region_managed_instance_group(instance_group_manager_client, project.project_id, region, instance_group_name)



# create region instance group managers client 
def create_region_instance_group_managers_client(project):
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return compute_v1.RegionInstanceGroupManagersClient(credentials=credentials)
    return compute_v1.RegionInstanceGroupManagersClient()

# private function
# update the managed instance group
def __update_region_managed_instance_group(instance_group_manager_client, project_id, region, instance_group_name, instance_template):
    logger.info(f"Updating managed instance group {instance_group_name}")
    # create a patch request to update the instance group manager with new instance template
    patch_request = compute_v1.PatchRegionInstanceGroupManagerRequest(
        project=project_id,
        region=region,
        instance_group_manager=instance_group_name,
        instance_group_manager_resource={
            "versions": [
                compute_v1.InstanceGroupManagerVersion(
                    instance_template=instance_template.self_link,
                    name="0-{}".format(int(time.time())),
                )
            ],
            "update_policy": {
                "minimal_action": "REPLACE",
                "most_disruptive_allowed_action": "REPLACE",
                "replacement_method": "RECREATE",
                "type": "OPPORTUNISTIC",
                "max_surge": {"fixed": 0},
            }
        },
    )

    # update instance group manager
    operation = instance_group_manager_client.patch(request=patch_request)

    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project_id)
    except Exception as e:
        logger.error(f"Error updating managed instance group: {e}")
        raise e
    logger.success(f"Managed instance group {instance_group_name} updated")

    # get instance group manager
    instance_group_manager = instance_group_manager_client.get(
        project=project_id, region=region, instance_group_manager=instance_group_name
    )    
    # return instance group manager
    return instance_group_manager

# Private function
# create managed instance group 
def __create_region_managed_instance_group(instance_group_manager_client, project_id, region, instance_group_name, instance_template):
    logger.info(f"Creating managed instance group {instance_group_name} with zero instances")
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


def __get_region_managed_instance_group(instance_group_manager_client, project_id, region, instance_group_name):
    logger.info("Checking if the managed instance group exists ...")
    # get instance group manager
    try:
        instance_group_manager = instance_group_manager_client.get(
            project=project_id, region=region, instance_group_manager=instance_group_name
        )
        logger.debug("Managed instance group exists")
        return instance_group_manager
    except Exception as e:
        logger.error(e)
        return None


# adding custom instances to the managed instance group 
def __region_adding_instances(
    instance_group_manager_client,
    project_id, region, instance_group_manager, size
    ):
    logger.debug(f"Adding {size} instances to the managed instance group {instance_group_manager.name}")
    # creating the master node first 
    logger.debug(f"Creating master node {instance_group_manager.name}-000")
    # create an instance group managers create instance request
    create_master_instance_request = compute_v1.CreateInstancesRegionInstanceGroupManagerRequest(
        project=project_id,
        region=region,
        instance_group_manager=instance_group_manager.name,
        region_instance_group_managers_create_instances_request_resource={
            "instances": [
                {
                    # format the name to 3 digits 
                    "name": f"{instance_group_manager.name}-{0:03d}"
                }
            ]
        },
    )

    # create instances 
    operation = instance_group_manager_client.create_instances(
        request=create_master_instance_request
    )
    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project_id)
    except Exception as e:
        logger.error(f"Error creating instances: {e}")
        raise e
    logger.success(f"Master node created {instance_group_manager.name}-000")
    if size > 1:
        # get full hostname of the master node 
        nodes = __list_region_instances(instance_group_manager_client, project_id, region, instance_group_manager.name)
        master_node = list(nodes)[0]
        master_node_hostname = master_node.instance.split("/")[-1]
        # get zone 
        master_node_zone = master_node.instance.split("/")[-3]
        full_master_hostname = f"{master_node_hostname}.{master_node_zone}.c.{project_id}.internal"
        logger.debug(f"Master node hostname: {full_master_hostname}")

        create_instance_request = compute_v1.CreateInstancesRegionInstanceGroupManagerRequest(
            project=project_id,
            region=region,
            instance_group_manager=instance_group_manager.name,
            region_instance_group_managers_create_instances_request_resource={
                "instances": [
                    {
                        # format the name to 3 digits 
                        "name": f"{instance_group_manager.name}-{instance_range:03d}",
                        # set custom metadata
                        "preserved_state": {
                            "metadata":
                                {
                                    "master_node_hostname": full_master_hostname
                                }
                        },
                    }
                    for instance_range in range(1, size)
                ],
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

   



# applying updates_to_instances
def __apply_updates_to_instances(instance_group_manager_client, project, region, instance_group_manager):
    # get the list of instances in the instance group manager 
    # then loop over the instances and apply update to each instance 
    # check with the serial port output to verify that the startup script worked successfully.
    # if the startup script failed, the serial port output will contain the error message.

    # get the list of instances in the instance group manager
    managed_instances = __list_region_instances(instance_group_manager_client, project.project_id, region, instance_group_manager.name)
    # loop over the instances and apply update to each instance
    for managed_instance in managed_instances:
        logger.debug(f"Applying updates to instance {managed_instance.instance}")
        # create an instance group managers apply updates request
        apply_updates_request = compute_v1.ApplyUpdatesToInstancesRegionInstanceGroupManagerRequest(
            project=project.project_id,
            region=region,
            instance_group_manager=instance_group_manager.name,
            region_instance_group_managers_apply_updates_request_resource={
                "instances": [managed_instance.instance]
            },
        )
        # apply updates to instances
        operation = instance_group_manager_client.apply_updates_to_instances(
            request=apply_updates_request
        )
        # wait for operation to complete
        try:
            wait_for_extended_operation(operation, project.project_id)
        except Exception as e:
            logger.error(f"Error applying updates to instances: {e}")
            raise e
        logger.success(f"Updates applied to instance {managed_instance.instance}")
        
        # get instance name and zone from the url 
        instance_name = managed_instance.instance.split("/")[-1]
        instance_zone = managed_instance.instance.split("/")[-3]

        logger.debug("Waiting for the startup script to finish")
        while True:    
            time.sleep(60)
            logger.debug("Waiting for the startup script to finish")
            # get the serial port output of the instance
            output = get_instance_serial_output(
                project,
                instance_zone,
                instance_name
            )
            # use regex to get startup-script-url status code 
            status_code = re.findall(r"startup-script-url exit status (\d+)", output)
            print(status_code)
            if len(status_code) >= 1:
                break
        if status_code[-1] != '0':
            logger.error("The startup script url returned an execution error")
            logger.error("Stopping the update script")
            return 
    






# scaling up the mig or down
def __region_scaling_mig(
    instance_group_manager_client,
    project_id, region, instance_group_manager, size, wanted_size
    ):
    logger.debug(f"Scaling managed instance group {instance_group_manager.name} from {size} to {wanted_size} instances")
    if size < wanted_size:  
        # get full hostname of the master node 
        nodes = __list_region_instances(instance_group_manager_client, project_id, region, instance_group_manager.name)
        master_node = list(nodes)[0]
        master_node_hostname = master_node.instance.split("/")[-1]
        # get zone 
        master_node_zone = master_node.instance.split("/")[-3]
        full_master_hostname = f"{master_node_hostname}.{master_node_zone}.c.{project_id}.internal"
        logger.debug(f"Master node hostname: {full_master_hostname}")
        # creating the master node first 
        # create an instance group managers create instance request
        create_instance_request = compute_v1.CreateInstancesRegionInstanceGroupManagerRequest(
            project=project_id,
            region=region,
            instance_group_manager=instance_group_manager.name,
            region_instance_group_managers_create_instances_request_resource={
                "instances": [
                    {
                        # format the name to 3 digits 
                        "name": f"{instance_group_manager.name}-{instance_range:03d}",
                        # set custom metadata
                        "preserved_state": {
                            "metadata":
                                {
                                    "master_node_hostname": full_master_hostname
                                }
                        }
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
        managed_instances =  list_region_instances(instance_group_manager_client, project_id, region, instance_group_manager.name)
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
def __list_region_instances(instance_group_manager_client, project_id, region, instance_group_name):
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


# delete regional managed instance group 
def __delete_region_managed_instance_group(instance_group_manager_client, project_id, region, instance_group_name):
    # create instance group manager request
    instance_group_manager_request = compute_v1.DeleteRegionInstanceGroupManagerRequest(
        project=project_id, region=region, instance_group_manager=instance_group_name
    )
    # delete instance group manager
    operation = instance_group_manager_client.delete(
        request=instance_group_manager_request
    )
    # wait for operation to complete
    try:
        wait_for_extended_operation(operation, project_id)
    except Exception as e:
        logger.error(f"Error deleting instance group manager: {e}")
        raise e
    logger.success(f"Instance group manager {instance_group_name} deleted")



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


    # create stateful policy for additional disks without boot disk
    stateful_policy = compute_v1.StatefulPolicy()
    stateful_policy.preserved_state = compute_v1.StatefulPolicyPreservedState()
    stateful_policy.preserved_state.disks = {}
    for disk in instance_template.properties.disks:
        if disk.boot == False:
            stateful_policy.preserved_state.disks[disk.device_name] = compute_v1.StatefulPolicyPreservedStateDiskDevice(auto_delete="never")

    # set target shape 
    distribution_policy.target_shape = "BALANCED"

    instance_group_manager_request.instance_group_manager_resource = compute_v1.InstanceGroupManager(
        name=instance_group_name,
        base_instance_name=instance_group_name,
        instance_template=instance_template.self_link,
        target_size=target_size,
        # add stateful policy to instance group manager
        stateful_policy=stateful_policy,
        # set distribution policy to the MIG 
        distribution_policy=distribution_policy,
        # set update policy 
        update_policy=compute_v1.InstanceGroupManagerUpdatePolicy(
            type="OPPORTUNISTIC",
            replacement_method="RECREATE",
            max_surge=compute_v1.FixedOrPercent(
                fixed=0
            ),
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




