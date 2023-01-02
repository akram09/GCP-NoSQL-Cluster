import argparse


# Parse cluster definition arguments 
def parse_cluster_args():
    parser = argparse.ArgumentParser(description='Couchbase cluster setup over GCP')

    parser.add_argument('--cluster-name', dest='cluster_name', required=True, help='Name of the cluster')
    # cluster size 
    parser.add_argument('--cluster-size', dest='cluster_size', required=True, help='Number of nodes in the cluster')
    # machine type with default value 
    parser.add_argument('--machine-type', dest='machine_type', default='e2-micro', help='Machine type for the cluster')
    # disk size with default value
    parser.add_argument('--disk-size', dest='disk_size', default='10', help='Disk size for the cluster')
    # disk type with default value
    parser.add_argument('--disk-type', dest='disk_type', default='pd-standard', help='Disk type for the cluster')
    # machine image with default value 
    parser.add_argument('--machine-image', dest='machine_image', default='projects/debian-cloud/global/images/family/debian-11', help='Machine image for the cluster')
    # cloud storage bucket
    parser.add_argument('--bucket', dest='bucket', help='Cloud storage bucket to store the cluster init scripts')

    return parser.parse_args()

    


