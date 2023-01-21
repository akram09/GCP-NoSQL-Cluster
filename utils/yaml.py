from loguru import logger
import yaml
from entities.cluster import ClusterParams
from entities.storage import GCPStorageParams
from entities.template import TemplateParams
from entities.couchbase import CouchbaseParams

# Parse cluster arguments from yaml file
def parse_from_yaml(yaml_file: str):
    logger.info(f"Reading cluster definition from {yaml_file}")
    # read the yaml file
    with open(yaml_file, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)
            exit(1)

    if 'cluster' not in data:
        logger.error("Yaml file not well formatted, please follow the standard format")
        exit(0)
    
    if 'storage' not in data['cluster']:
        logger.error("Storage bucket is missing from the yaml file")
        exit(0)

    # Parse cluster important params
            
    # verify if the yaml file has attributes: cluster_name, cluster_size, bucket
    if data['cluster']['name'] == None:
        logger.error("Cluster name is missing from the yaml file")
        exit(0)
    if data['cluster']['size'] == None:
        logger.error("Cluster size is missing from the yaml file")
        exit(0)
    if data['cluster']['region'] == None:
        logger.error("Cluster region is missing from the yaml file")
        exit(0)
    if data['cluster']['storage']['bucket'] == None:
        logger.error("Bucket is missing from the yaml file")
        exit(0)
   
    # creat a cluster object from the properties
    cluster_name = data['cluster']['name']
    cluster_size = data['cluster']['size']
    cluster_region = data['cluster']['region']
    bucket = data['cluster']['storage']['bucket']

    storage = GCPStorageParams(bucket)


    cluster = ClusterParams(cluster_name, cluster_size, cluster_region, storage)

    if 'name' not in data['cluster']['template']: 
        template_name = f"template-{self.cluster_name}"
    else:
        template_name = data['cluster']['template']['name'] 

    template_params =  TemplateParams(template_name)

    if 'template' in data['cluster']:
        # parse template values
        template = data['cluster']['template'] 
        if 'machine_type' in template:
            template_params.machine_type = template['machine_type']
        if 'disk_size' in template:
            template_params.disk_size = template['disk_size']
        if 'disk_type' in template:
            template_params.disk_type = template['disk_type']
        if 'extra_disk_type' in template:
            template_params.extra_disk_type = template['extra_disk_type']
        if 'extra_disk_size' in template:
            template_params.extra_disk_size = template['extra_disk_size']
        if 'image_project' in template:
            template_params.image_project = template['image_project']
        if 'image_family' in template:
            template_params.image_family = template['image_family']
    
    cluster.template = template_params

    couchbase_params = CouchbaseParams() 
    if 'couchbase' in data['cluster']: 
        couchbase = data['cluster']['couchbase'] 
        # parse couchbase values
        if 'username' in couchbase:
            couchbase_params.username = couchbase['username']
        if 'password' in couchbase:
            couchbase_params.password = couchbase['password']

    cluster.couchbase_params = couchbase_params

    return cluster
