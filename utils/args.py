import argparse
from loguru import logger
from entities.cluster import ClusterParams
from entities.storage import GCPStorageParams
from entities.template import TemplateParams
from entities.couchbase import CouchbaseParams
from utils.yaml import parse_from_yaml

# Parse arguments 
def parse_args_from_cmdline():
    parser = argparse.ArgumentParser(description='Management of a couchbase cluster over gcp with the used of managed instance group')

    # add a new subparser for the create cmd 
    subparsers = parser.add_subparsers(help='Different commands for lifecycle management')
    # add arguments for the create subcommand
    add_create_cmd_args(subparsers)

    namespace = parser.parse_args()
    
    # if no command is specified, then print the help 
    if not hasattr(namespace, 'command'):
        parser.print_help()
        exit(0)
    return namespace



# Add "create"  subcommand and arguments
def add_create_cmd_args(subparsers):
    create_subparser = subparsers.add_parser('create', help='Create and deploy a couchbase cluster')
    
    create_subparser.add_argument('--project-id', dest='project_id', help='The id of GCP project, this argument can be also specified with the "GOOGLE_CLOUD_PROJECT" environment variable.')
    # yaml file
    create_subparser.add_argument('--yaml-file', dest='yaml_file', help='name of the yaml file with cluster definition')
    # authentifcation type 
    create_subparser.add_argument('--authentication-type', default="service-account" ,dest='authentication_type', help="The type of authentication to be used either service-account or oauth")
    # cluster name
    create_subparser.add_argument('--cluster-name', dest='cluster_name', help='Name of the cluster')
    # cluster size 
    create_subparser.add_argument('--cluster-size', dest='cluster_size', help='Number of nodes in the cluster')
    # cloud storage bucket
    create_subparser.add_argument('--bucket', dest='bucket', help='Cloud storage bucket to store the cluster init scripts')
    # cluster region
    create_subparser.add_argument('--region', dest='region', help='Region where the cluster will be created')
    # machine type with default value 
    create_subparser.add_argument('--machine-type', dest='machine_type', help='Machine type for the cluster')
    # disk size with default value
    create_subparser.add_argument('--disk-size', dest='disk_size', help='Disk size for the cluster')
    # disk type with default value
    create_subparser.add_argument('--disk-type', dest='disk_type', help='Disk type for the cluster')
    # extra disk tyoe 
    create_subparser.add_argument('--extra-disk-type', dest='extra_disk_type', help='Extra disk type')
    # extra disk size
    create_subparser.add_argument('--extra-disk-size', dest='extra_disk_size', help='Extra disk size')
    # machine image project with default value 
    create_subparser.add_argument('--image-project', dest='image_project', help='Machine image project for the cluster')
    # Template name
    create_subparser.add_argument('--template-name', dest='template name, this parameter needs to be present')
    # machine image family with default value 
    create_subparser.add_argument('--image-family', dest='image_family', help='Machine image family project for the cluster')
    # cluster username with default value
    create_subparser.add_argument('--cluster-username', dest='cluster-username', help='Username for the cluster')
    # cluster password with default value
    create_subparser.add_argument('--cluster-password', dest='cluster-password', help='Password for the cluster')

    # set the function to be called when running the sub command
    create_subparser.set_defaults(command="create")



def required_error_msg(arg):
    command_msg = '''usage: main.py create  [-h] --yaml-file YAML_FILE [--cluster-name CLUSTER_NAME] [--cluster-size CLUSTER_SIZE] [--bucket BUCKET] [--machine-type MACHINE_TYPE] [--disk-size DISK_SIZE] [--template-name TEMPLATE_NAME]
[--disk-type DISK_TYPE] [--image-project IMAGE_PROJECT] [--image-family IMAGE_FAMILY] [ --cluster-username CLUSTER_USERNAME] [--cluster-password CLUSTER_PASSWORD]
        '''
    logger.error(f"{command_msg}\nmain.py: error: the following arguments are required: --{'-'.join(arg.split('_'))}")

# Create cluster object from arguments
def cluster_from_args(args: argparse.Namespace) -> ClusterParams:
    if args.yaml_file != None:
        return parse_from_yaml(args.yaml_file)
    else:
        logger.info("Creating cluster from arguments")
        if args.cluster_name == None:
            required_error_msg("cluster_name")
            exit(0)
        if args.cluster_size == None:
            required_error_msg("cluster_size")
            exit(0)
        if args.region == None:
            required_error_msg("region")
            exit(0)
        if args.bucket == None:
            required_error_msg("bucket")
            exit(0)        
        cluster = ClusterParams(args.cluster_name, args.cluster_size, agrs.region)

        storage = Storage(args.bucket)
        cluster.storage = storage

        if args.template_name == None:
            template_name = f"template-{args.cluster_name}"
        else:
            template_name = agrs.template_name

        template = TemplateParams(template_name, args.machine_type, args.disk_size, args.disk_type,args.extra_disk_type, args.extra_disk_size, args.image_project, args.image_family)
        cluster.template = template
        
        couchbase_params = CouchbaseParams(args.cluster_username, args.cluster_password)
        cluster.couchbase_params = couchbase_params
        logger.info(f"ClusterParams definition: {cluster}")
        return cluster
