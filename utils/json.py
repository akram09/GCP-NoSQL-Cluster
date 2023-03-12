from loguru import logger
import json
from shared.entities.cluster import ClusterParams
from shared.entities.storage import GCPStorageParams
from shared.entities.template import TemplateParams
from shared.entities.couchbase import CouchbaseParams
from utils.exceptions import JsonParseException


def parse_cluster_def_from_json(json_dict, cluster_name):
    logger.info(f"Reading cluster definition from Json dict")
    if 'cluster' not in json_dict:
        logger.error("Key 'cluster' not found in the json object. The json is mal formed")
        raise JsonParseException("Key 'cluster' not found in the json object. The json is mal formed")
      
    if 'storage' not in json_dict['cluster']:
        logger.error("Key 'cluster.storage' not found in the json object. The json is mal formed")
        raise JsonParseException("Key 'cluster.storage' not found in the json object. The json is mal formed")

            
    if json_dict['cluster']['size'] == None:
        logger.error("Cluster size is missing from the json object")
        raise JsonParseException("Cluster size is missing from the json object")
    if json_dict['cluster']['region'] == None:
        logger.error("Cluster region is missing from the json object")
        raise JsonParseException("Cluster region is missing from the json object")
    if json_dict['cluster']['storage']['bucket'] == None:
        logger.error("Cluster storage bucket is missing from the json object")
        raise JsonParseException("Cluster storage bucket is missing from the json object")
   
    # creat a cluster object from the properties
    cluster_size = json_dict['cluster']['size']
    cluster_region = json_dict['cluster']['region']
    bucket = json_dict['cluster']['storage']['bucket']

    storage = GCPStorageParams(bucket)


    cluster = ClusterParams(cluster_name, cluster_size, cluster_region, storage)

    # parse template values
    if 'template' in json_dict['cluster'] and 'name' in json_dict['cluster']['template']:
        template_name = json_dict['cluster']['template']['name']
    else:
        template_name = f"template-{cluster_name}"
    template_params =  TemplateParams(template_name)

    if 'template' in json_dict['cluster']:
        # parse template values
        template = json_dict['cluster']['template'] 
        if 'machine_type' in template:
            template_params.machine_type = template['machine_type']
        if 'image_project' in template:
            template_params.image_project = template['image_project']
        if 'image_family' in template:
            template_params.image_family = template['image_family']
        if 'disks' in template:
            template_params.set_disks(template['disks'])
        else:
            # if no disks are defined, use the default one
            template_params.set_disks([{'size': 10, 'type': 'pd-standard',  'boot': True}])

    
    cluster.template = template_params

    couchbase_params = CouchbaseParams() 
    if 'couchbase' in json_dict['cluster']: 
        couchbase = json_dict['cluster']['couchbase'] 
        # parse couchbase values
        if 'username' in couchbase:
            couchbase_params.username = couchbase['username']
        if 'password' in couchbase:
            couchbase_params.password = couchbase['password']
    else:
        couchbase_params = None

    cluster.couchbase_params = couchbase_params

    return cluster
