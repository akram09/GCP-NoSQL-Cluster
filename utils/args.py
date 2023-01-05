import argparse

# Parse arguments 
def parse_cluster_args() -> argparse.Namespace:
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

