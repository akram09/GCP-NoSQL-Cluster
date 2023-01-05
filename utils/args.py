import argparse
from utils.gcp import get_image_from_family
from lib.template import create_template
from lib.storage import upload_startup_script
import yaml

# Parse arguments 
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Couchbase cluster setup over GCP')
    # yaml file
    parser.add_argument('--yaml-file', dest='yaml_file', help='name of the yaml file with cluster definition')
    # cluster name
    parser.add_argument('--cluster-name', dest='cluster_name', help='Name of the cluster')
    # cluster size 
    parser.add_argument('--cluster-size', dest='cluster_size', help='Number of nodes in the cluster')
    # cloud storage bucket
    parser.add_argument('--bucket', dest='bucket', help='Cloud storage bucket to store the cluster init scripts')
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
    # cluser username with default value
    parser.add_argument('--cluster-username', dest='cluster-username', default='admin', help='Username for the cluster')
    # cluster password with default value
    parser.add_argument('--cluster-password', dest='cluster-password', default='password', help='Password for the cluster')

    return parser.parse_args()


# create ClusterArgs class that parses cluster arguments from yaml file if it is given or from args
class ClusterArgs:
    def __init__(self, args: argparse.Namespace):

        if args.yaml_file != None:
            self.parse_from_yaml(args.yaml_file)
        else:
            if args.cluster_name == None:
                self.required_error_msg("cluster_name")
                exit(0)
            if args.cluster_size == None:
                self.required_error_msg("cluster_size")
                exit(0)
            if args.bucket == None:
                self.required_error_msg("bucket")
                exit(0)
            self.parse_from_args(args)
    
    def parse_from_args(self, args: argparse.Namespace):
        self.cluster_name = args.cluster_name
        self.cluster_size = args.cluster_size
        self.machine_type = args.machine_type
        self.disk_size = args.disk_size
        self.disk_type = args.disk_type
        self.image_project = args.image_project
        self.image_family = args.image_family
        self.bucket = args.bucket
        self.cluster_name_username = args.cluster_username
        self.cluster_name_password = args.cluster_password
    
    def parse_from_yaml(self, yaml_file: str):
        # read the yaml file
        with open(yaml_file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                
        # verify if the yaml file has attributes: cluster_name, cluster_size, bucket
        if data['cluster_name'] == None:
            print("cluster_name is not defined in the yaml file")
            exit(0)
        if data['cluster_size'] == None:
            print("cluster_size is not defined in the yaml file")
            exit(0)
        if data['bucket'] == None:
            print("bucket is not defined in the yaml file")
            exit(0)
        
        self.cluster_name = data['cluster_name']
        self.cluster_size = data['cluster_size']
        self.machine_type = data['machine_type']
        self.disk_size = data['disk_size']
        self.disk_type = data['disk_type']
        self.image_project = data['image_project']
        self.image_family = data['image_family']
        self.bucket = data['bucket']
        self.cluster_username = data['cluster_username']
        self.cluster_password = data['cluster_password']

        # method that prints the cluster arguments
    def __str__(self):
        return f"cluster_name: {self.cluster_name}, cluster_size: {self.cluster_size}, machine_type: {self.machine_type}, disk_size: {self.disk_size}, disk_type: {self.disk_type}, image_project: {self.image_project}, image_family: {self.image_family}, bucket: {self.bucket}"

    def required_error_msg(self, arg):
        command_msg = '''usage: main.py [-h] --yaml-file YAML_FILE [--cluster-name CLUSTER_NAME] [--cluster-size CLUSTER_SIZE] [--bucket BUCKET] [--machine-type MACHINE_TYPE] [--disk-size DISK_SIZE]
    [--disk-type DISK_TYPE] [--image-project IMAGE_PROJECT] [--image-family IMAGE_FAMILY] [ --cluster-username CLUSTER_USERNAME] [--cluster-password CLUSTER_PASSWORD]
            '''
        print(f"{command_msg}\nmain.py: error: the following arguments are required: --{'-'.join(arg.split('_'))}")
