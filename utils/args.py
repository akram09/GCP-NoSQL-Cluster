import argparse
import yaml
from entities.cluster import Cluster
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
    # cluster region
    parser.add_argument('--region', dest='region', help='Region where the cluster will be created')
    # machine type with default value 
    parser.add_argument('--machine-type', dest='machine_type', help='Machine type for the cluster')
    # disk size with default value
    parser.add_argument('--disk-size', dest='disk_size', help='Disk size for the cluster')
    # disk type with default value
    parser.add_argument('--disk-type', dest='disk_type', help='Disk type for the cluster')
    # machine image project with default value 
    parser.add_argument('--image-project', dest='image_project', help='Machine image project for the cluster')
    # machine image family with default value 
    parser.add_argument('--image-family', dest='image_family', help='Machine image family project for the cluster')
    # cluster username with default value
    parser.add_argument('--cluster-username', dest='cluster-username', help='Username for the cluster')
    # cluster password with default value
    parser.add_argument('--cluster-password', dest='cluster-password', help='Password for the cluster')

    return parser.parse_args()



# Parse cluster arguments from yaml file

def parse_from_yaml(yaml_file: str):
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
   
    # creat a cluster object from the properties
    cluster_name = data['cluster_name']
    cluster_size = data['cluster_size']
    bucket = data['bucket']

    cluster = Cluster(cluster_name, cluster_size, bucket)
    # set the optional properties
    if 'machine_type' in data:
        cluster.machine_type = data['machine_type']
    if 'disk_size' in data:
        cluster.disk_size = data['disk_size']
    if 'disk_type' in data:
        cluster.disk_type = data['disk_type']
    if 'image_project' in data:
        cluster.image_project = data['image_project']
    if 'image_family' in data:
        cluster.image_family = data['image_family']
    if 'cluster_username' in data:
        cluster.cluster_username = data['cluster_username']
    if 'cluster_password' in data:
        cluster.cluster_password = data['cluster_password']
    if 'cluster_region' in data:
        cluster.cluster_region = data['cluster_region']

    return cluster

def required_error_msg(arg):
    command_msg = '''usage: main.py [-h] --yaml-file YAML_FILE [--cluster-name CLUSTER_NAME] [--cluster-size CLUSTER_SIZE] [--bucket BUCKET] [--machine-type MACHINE_TYPE] [--disk-size DISK_SIZE]
[--disk-type DISK_TYPE] [--image-project IMAGE_PROJECT] [--image-family IMAGE_FAMILY] [ --cluster-username CLUSTER_USERNAME] [--cluster-password CLUSTER_PASSWORD]
        '''
    print(f"{command_msg}\nmain.py: error: the following arguments are required: --{'-'.join(arg.split('_'))}")

# Create cluster object from arguments
def cluster_from_args(args: argparse.Namespace) -> Cluster:
    if args.yaml_file != None:
        return parse_from_yaml(args.yaml_file)
    else:
        if args.cluster_name == None:
            required_error_msg("cluster_name")
            exit(0)
        if args.cluster_size == None:
            required_error_msg("cluster_size")
            exit(0)
        if args.bucket == None:
            required_error_msg("bucket")
            exit(0) 
        return Cluster(args.cluster_name, args.cluster_size, args.machine_type, args.disk_size, args.disk_type, args.image_project, args.image_family, args.bucket, args.cluster_username, args.cluster_password, args.cluster_region)




