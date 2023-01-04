import argparse
from utils.gcp import get_image_from_family
from lib.template import create_template
from lib.storage import upload_startup_script
import yaml

# Parse cluster definition arguments 
def parse_cluster_args():
    parser = argparse.ArgumentParser(description='Couchbase cluster setup over GCP')
    # yaml file
    parser.add_argument('--yaml-file', dest='yaml_file', help='name of the yaml file with cluster definition')
    # cluster name
    parser.add_argument('--cluster-name', dest='cluster_name', help='Name of the cluster')
    # cluster size 
    parser.add_argument('--cluster-size', dest='cluster_size', help='Number of nodes in the cluster')
    # machine type with default value 
    parser.add_argument('--machine-type', dest='machine_type', default='e2-micro', help='Machine type for the cluster')
    # disk size with default value
    parser.add_argument('--disk-size', dest='disk_size', default='10', help='Disk size for the cluster')
    # disk type with default value
    parser.add_argument('--disk-type', dest='disk_type', default='pd-standard', help='Disk type for the cluster')
    # machine image project with default value 
    parser.add_argument('--image-project', dest='image_project', default='debian-cloud', help='Machine image project for the cluster')
    # machine image family with default value 
    parser.add_argument('--image-family', dest='image_family', default='debian-11', help='Machine image family project for the cluster')
    # cloud storage bucket
    parser.add_argument('--bucket', dest='bucket', help='Cloud storage bucket to store the cluster init scripts')

    return parser.parse_args()


def create_template_from_args(
    project_id: str,
    zone:str,
    template_name: str,
    args: argparse.Namespace
    ):
    
    #Get the machine image from the project and family
    machine_image = get_image_from_family(
        project=args.image_project, family=args.image_family
    )


    # upload the startup script to the bucket
    startup_script_url = upload_startup_script(args.image_family, args.bucket)

    print(startup_script_url)
    # template = create_template(
    #     project_id,
    #     zone,
    #     template_name,
    #     args.machine_type,
    #     machine_image,
    #     args.disk_type,
    #     args.disk_size,
    #     startup_script_url
    # )
    # 
    # return template

    
# function that creates template from yaml file instead of args
def create_template_from_yaml(
    project_id: str,
    zone:str,
    template_name: str,
    yaml_file: str
    ):
    
    # read the yaml file
    with open(yaml_file, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # verify if the yaml file has attributes: cluster_name, cluster_size, bucket
    if data['cluster_name'] == None:
       raise Exception("cluster_name is not defined in the yaml file")
    if data['cluster_size'] == None:
     raise Exception("cluster_size is not defined in the yaml file")
    if data['bucket'] == None:
        raise Exception("bucket is not defined in the yaml file")


    #Get the machine image from the project and family
    machine_image = get_image_from_family(
        project=data['image_project'], family=data['image_family']
    )

    # upload the startup script to the bucket
    startup_script_url = upload_startup_script(data['image_family'], data['bucket'])

    template = create_template(
        project_id,
        zone,
        template_name,
        data['machine_type'],
        machine_image,
        data['disk_type'],
        data['disk_size'],
        startup_script_url
    )
    
    return template 
