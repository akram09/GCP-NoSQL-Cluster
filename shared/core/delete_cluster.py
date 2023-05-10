from shared.lib.regional_managed_instance import delete_region_managed_instance_group, get_region_managed_instance_group
from shared.core.instance_template_operations import delete_instance_template



def delete_cluster(gcp_project, cluster_name, region):
    """
    Function to delete a cluster, this involves:
    - Deleting the regional managed instance group 
    - Deleting the instance template 
    """
    # Get managed instance group object 
    mig = get_region_managed_instance_group(gcp_project, region, cluster_name)
    # Get instance template name 
    instance_template = mig.instance_template.split('/')[-1]
    # Delete the regional managed instance group
    delete_region_managed_instance_group(gcp_project, region, cluster_name)
    # Delete the instance template
    delete_instance_template(gcp_project, instance_template)

