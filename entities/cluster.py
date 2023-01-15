from loguru import logger
import uuid
from utils.gcp import get_image_from_family
from lib.storage import upload_startup_script
from lib.vm_instance import get_instances_from_managed_instances
from lib.template import create_template, get_instance_template, update_template
from lib.firewall import create_firewall_rule, check_firewall_rule
from lib.managed_instance import create_managed_instance_group, list_instances
from lib.regional_managed_instance import create_region_managed_instance_group, list_region_instances, region_adding_instances, get_region_managed_instance_group, region_scaling_mig
from utils.couchbase import create_couchbase_cluster

# Cluster class 
class Cluster:

    def __init__(self, cluster_name, cluster_size, bucket, machine_type="e2-micro", disk_size=10, disk_type="pd-standard", extra_disk_type="pd-standard", extra_disk_size=20, image_project="debian-cloud", image_family="debian-11",  cluster_username="admin", cluster_password="password", cluster_region=None):
        self.cluster_name = cluster_name
        self.cluster_size = cluster_size
        self.cluster_region = cluster_region
        self.machine_type = machine_type
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.extra_disk_size = extra_disk_size
        self.extra_disk_type = extra_disk_type
        self.image_project = image_project
        self.image_family = image_family
        self.bucket = bucket
        self.cluster_username = cluster_username
        self.cluster_password = cluster_password
    
    # deploy cluster on gcp 
    def deploy_cluster_gcp(self, project): 
        logger.info(f"Deploying cluster {self.cluster_name} on GCP ...")
        #Create instance templace
        template_name = f"template-{self.cluster_name}"

        #Get the machine image from the project and family
        machine_image = get_image_from_family(self.image_project, self.image_family)


        # upload the startup script to the bucket
        startup_script_url = upload_startup_script(project.project_id, self.image_family, self.bucket, self.cluster_username, self.cluster_password, self.cluster_name, self.cluster_size)

        template = get_instance_template(project.project_id, template_name)
        # check if there is a template existing 
        if template is None: 
            logger.info(f"Instance template {template_name} does not exist, creating ...")
            # create instance template
            template = create_template(
                project.project_id,
                project.zone,
                template_name,
                self.machine_type,
                machine_image,
                self.disk_type,
                self.disk_size,
                self.extra_disk_type,
                self.extra_disk_size,
                startup_script_url
            )
        else:
            logger.debug(f"Instance template {template_name} already exists")
            # update the instance template 
            update_template(
                project.project_id,
                template,
                project.zone,
                self.machine_type,
                machine_image,
                self.disk_type,
                self.disk_size,
                self.extra_disk_type,
                self.extra_disk_size,
                startup_script_url 
            )
        
        #if the cluster region is specified then create regional managed instance 
        if self.cluster_region != None:
            # check if the managed instance group exists
            mig = get_region_managed_instance_group(project.project_id, self.cluster_region, self.cluster_name)
            if mig is None: 
                logger.debug(f"Creating regional managed instance group {self.cluster_name}")
                mig = create_region_managed_instance_group(project.project_id, self.cluster_region, self.cluster_name, template.name)
                region_adding_instances(project.project_id, self.cluster_region, mig, self.cluster_size)
            else:
                logger.debug(f"Regional managed instance group {self.cluster_name} already exists")
                logger.debug(f"We will update the size of the regional managed instance group {self.cluster_name} to {self.cluster_size}")
                region_scaling_mig(project.project_id, self.cluster_region, mig, mig.target_size, self.cluster_size)
     
        else: 
            logger.debug(f"Creating zone managed instance group {self.cluster_name}")
            #Create instance group
            create_managed_instance_group(project.project_id, self.cluster_region, self.cluster_name, template.name, self.cluster_size)

        logger.info("Checking firewall rules")
        # Check if the firewall rule exists
        if check_firewall_rule(project.project_id, self.cluster_name+"-firewall"):
            logger.debug(f"Firewall rule {self.cluster_name}-firewall already exists")
        else:
            logger.debug(f"Creating firewall rule {self.cluster_name}-firewall")
            create_firewall_rule(project.project_id, self.cluster_name+"-firewall")
            logger.success(f"Firewall rule {self.cluster_name}-firewall created")
        logger.success(f"Cluster {self.cluster_name} created successfully")


    # print cluster details
    def __str__(self):
        return f"Cluster Name: {self.cluster_name}  Cluster Size: {self.cluster_size}  Machine Type: {self.machine_type}  Disk Size: {self.disk_size}  Disk Type: {self.disk_type}  Image Project: {self.image_project}  Image Family: {self.image_family}  Bucket: {self.bucket}  Cluster Username: {self.cluster_username}  Cluster Password: {self.cluster_password}"

