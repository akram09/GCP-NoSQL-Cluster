import argparse
import yaml
import uuid
from utils.gcp import get_image_from_family
from lib.storage import upload_startup_script
from lib.template import create_template
from lib.firewall import create_firewall_rule, check_firewall_rule
from lib.managed_instance import create_managed_instance_group
from utils.couchbase import create_couchbase_cluster
# Cluster class 
class Cluster:

    def __init__(self, cluster_name, cluster_size, bucket, machine_type="e2-micro", disk_size="10", disk_type="pd-standard", image_project="debian-cloud", image_family="debian-11",  cluster_username="admin", cluster_password="password"):
        self.cluster_name = cluster_name
        self.cluster_size = cluster_size
        self.machine_type = machine_type
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.image_project = image_project
        self.image_family = image_family
        self.bucket = bucket
        self.cluster_username = cluster_username
        self.cluster_password = cluster_password
    
    # deploy cluster on gcp 
    def deploy_cluster_gcp(self, project): 
        #Create instance templace
        template_name = f"template-{uuid.uuid4()}"

        #Get the machine image from the project and family
        machine_image = get_image_from_family(self.image_project, self.image_family)


        # upload the startup script to the bucket
        startup_script_url = upload_startup_script(self.image_family, self.bucket)
        
        # create instance template
        template = create_template(
            project.project_id,
            project.zone,
            template_name,
            self.machine_type,
            machine_image,
            self.disk_type,
            self.disk_size,
            startup_script_url
        )
        
        #Create instance group
        create_managed_instance_group(project.project_id, project.zone, self.cluster_name, template.name, self.cluster_size)
        
        # Check if the firewall rule exists
        if check_firewall_rule(project.project_id, self.cluster_name+"-firewall"):
            print("Firewall rule exists")
        else:
            print("Firewall rule does not exist")
            create_firewall_rule(project.project_id, self.cluster_name+"-firewall")

        # Create a cluster from the instance group 
        create_couchbase_cluster(project.project_id, project.zone, self.bucket, self.cluster_name, self.cluster_username, self.cluster_password)


    # print cluster details
    def __str__(self):
        return f"Cluster Name: {self.cluster_name}  Cluster Size: {self.cluster_size}  Machine Type: {self.machine_type}  Disk Size: {self.disk_size}  Disk Type: {self.disk_type}  Image Project: {self.image_project}  Image Family: {self.image_family}  Bucket: {self.bucket}  Cluster Username: {self.cluster_username}  Cluster Password: {self.cluster_password}"








