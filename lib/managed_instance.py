from lib.template import get_instance_template
from google.cloud import compute_v1
from utils.gcp import wait_for_extended_operation, get_image_from_family
from lib.storage import upload_startup_script
from lib.template import create_template
import uuid

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


    # create health check
    #health_check = create_health_check(project_id, "health-check-1", "http", 80, "/")

    instance_group_manager_request.instance_group_manager_resource = compute_v1.InstanceGroupManager(
        name=instance_group_name,
        base_instance_name=instance_group_name,
        instance_template=instance_template.self_link,
        target_size=target_size,
        #add stateful policy to instance group manager
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

        # add autohealing policy to instance group manager
        # auto_healing_policies=[
        #     compute_v1.InstanceGroupManagerAutoHealingPolicy(
        #         health_check=health_check['self_link'],
        #         initial_delay_sec=60,
        #     )
        # ],
    )

    
    # return instance group manager request
    return instance_group_manager_request
    

def create_cluster(project_id: str, zone: str, cluster_args):

    #Create instance templace
    template_name = f"template-{uuid.uuid4()}"

    #Get the machine image from the project and family
    machine_image = get_image_from_family(
        project=cluster_args.image_project, family=cluster_args.image_family
    )


    # upload the startup script to the bucket
    startup_script_url = upload_startup_script(cluster_args.image_family, cluster_args.bucket)

    # create instance template
    template = create_template(
        project_id,
        zone,
        template_name,
        cluster_args.machine_type,
        machine_image,
        cluster_args.disk_type,
        cluster_args.disk_size,
        startup_script_url
    )

    #Create instance group
    create_managed_instance_group(project_id, zone, cluster_args.cluster_name, template.name)