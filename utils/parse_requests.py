from loguru import logger
import json
from shared.entities.cluster import ClusterParams
from shared.entities.storage import GCPStorageParams
from shared.entities.template import TemplateParams
from shared.entities.couchbase import CouchbaseParams
from utils.exceptions import InvalidJsonException


def parse_cluster_def_from_json(cluster_dict):
    logger.info(f"Reading cluster definition from Json dict")
      
    if 'storage' not in cluster_dict:
        logger.error("Key 'storage' not found in the json object. The json is mal formed")
        raise InvalidJsonException("Key 'storage' not found in the json object. The json is mal formed")

    if 'name' not in cluster_dict:
        logger.error("Key 'name' not found in the json object. The json is mal formed")
        raise InvalidJsonException("Key 'name' not found in the json object. The json is mal formed")
    if cluster_dict['size'] == None:
        logger.error("Cluster size is missing from the json object")
        raise InvalidJsonException("Cluster size is missing from the json object")
    if cluster_dict['region'] == None:
        logger.error("Cluster region is missing from the json object")
        raise InvalidJsonException("Cluster region is missing from the json object")
    if cluster_dict['storage']['bucket'] == None:
        logger.error("Cluster storage bucket is missing from the json object")
        raise InvalidJsonException("Cluster storage bucket is missing from the json object")
   
    # creat a cluster object from the properties
    cluster_name = cluster_dict['name']
    cluster_size = cluster_dict['size']
    cluster_region = cluster_dict['region']
    bucket = cluster_dict['storage']['bucket']

    storage = GCPStorageParams(bucket)
    if 'type' in cluster_dict['storage']:
        storage.type = cluster_dict['storage']['type']


    cluster = ClusterParams(cluster_name, cluster_size, cluster_region, storage)
    # parse instance template params    
    if "template" in cluster_dict:
        cluster.template = parse_instance_template(cluster_dict["template"], cluster_name)
    else: 
        cluster.template = TemplateParams(f"template-{cluster_name}")

    couchbase_params = CouchbaseParams() 
    if 'couchbase' in cluster_dict: 
        couchbase = cluster_dict['couchbase'] 
        # parse couchbase values
        if 'username' in couchbase:
            couchbase_params.username = couchbase['username']
        if 'password' in couchbase:
            couchbase_params.password = couchbase['password']
    else:
        couchbase_params = None

    cluster.couchbase_params = couchbase_params

    return cluster

def parse_instance_template_from_json(instance_template_dict):
    return parse_instance_template(instance_template_dict, None)



def parse_instance_template(instance_template_dict, cluster_name):
    if instance_template_dict == None and cluster_name == None:
        raise InvalidJsonException("Instance Template params not specified")
    # parse template values
    if instance_template_dict != None and 'name' in instance_template_dict:
        template_name = instance_template_dict['name']
    else:
        template_name = f"template-{cluster_name}"
    template_params =  TemplateParams(template_name)

    if instance_template_dict:
        # parse template values
        template = instance_template_dict 
        if 'machine_type' in template:
            template_params.machine_type = template['machine_type']
        if 'image_project' in template:
            template_params.image_project = template['image_project']
        if 'image_family' in template:
            template_params.image_family = template['image_family']
        if 'region' in template: 
            template_params.region = template['region']
        if 'disks' in template:
            template_params.set_disks(template['disks'])
        else:
            # if no disks are defined, use the default one
            template_params.set_disks([{'size': 10, 'type': 'pd-standard',  'boot': True}])
        if 'labels' in template:
            labels = template['labels']
            if not isinstance(labels, list):
                raise InvalidJsonException("Cluster labels should be an array")
            for label in labels:
                if 'key' not in label or 'value' not in label: 
                    raise InvalidJsonException("Labels should have a key and a value")
            # map the labels list to a dict of key value pairs 
            labels  = dict(map(lambda label: (label['key'], label['value']), labels))
            template_params.labels = labels
        if 'startup_script_url' in template:
            template_params.startup_script_url = template['startup_script_url']
        if 'shutdown_script_url' in template:
            template_params.shutdown_script_url = template['shutdown_script_url']
    return template_params

