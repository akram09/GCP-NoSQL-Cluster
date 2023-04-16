from loguru import logger
from google.cloud import storage
import os
from jinja2 import Template
import google.oauth2.credentials
from utils.exceptions import GCPStorageBucketCreationFailedException, GCPUnsupportedOSFamilyException











def setup_cloud_storage(project, storage_params, region, key):
    # Create storage client
    storage_client = create_storage_client(project)

    logger.info("Checking if the bucket exists else creating the bucket...")
    # Create the bucket if not existed
    bucket = __create_bucket(storage_client, storage_params.bucket, region, key)

    logger.info("Assigning read storage role to the bucket...") 
    # Add Compute Engine default service account to the bucket
    # read member from environment variable
    member = {"user": os.environ['COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL']}
    role = "roles/storage.objectViewer"

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": [member]})

    bucket.set_iam_policy(policy)
    logger.debug(f"Added {member} to {bucket.name} with {role} role.")

    return bucket

def upload_scripts(project, bucket, template_params, cluster_params, secret_name):
    # create storage client 
    client = create_storage_client(project)

    # upload the startup script to the bucket
    startup_script_url = __upload_startup_script(client, project.project_id, template_params.image_family, bucket, cluster_params.name, cluster_params.size, secret_name)
    # upload the shutdown script to the bucket
    shutdown_script_url = __upload_shutdown_script(client, project.project_id, template_params.image_family, bucket)

    return {
        "startup_script_url": startup_script_url,
        "shutdown_script_url": shutdown_script_url
    }







# public function 
def create_bucket(project, bucket_name, location, key):
    storage_client = create_storage_client(project)
    return __create_bucket(storage_client, bucket_name, location, key)

# public function 
def list_buckets(project):
    storage_client = create_storage_client(project)
    return __list_buckets(storage_client)

# public function
def delete_bucket(project, bucket_name):
    storage_client = create_storage_client(project)
    return __delete_bucket(storage_client, bucket_name)

# public function
def upload_blob(project, bucket_name, source_file_name, destination_blob_name):
    storage_client = create_storage_client(project)
    return __upload_blob(storage_client, bucket_name, source_file_name, destination_blob_name)

# public function
def download_blob(project, bucket_name, source_blob_name, destination_file_name):
    storage_client = create_storage_client(project)
    return __download_blob(storage_client, bucket_name, source_blob_name, destination_file_name)

# public function
def list_blobs(project, bucket_name):
    storage_client = create_storage_client(project)
    return __list_blobs(storage_client, bucket_name)


# public function 
def upload_startup_script(project, image_family: str, bucket, cluster_name: str, cluster_size: int, secret_name: str):
    storage_client = create_storage_client(project)
    return __upload_startup_script(storage_client, project.project_id, image_family, bucket, cluster_name, cluster_size, secret_name)

# public function 
def upload_shutdown_script(project, image_family: str, bucket):
    storage_client = create_storage_client(project)
    return __upload_shutdown_script(storage_client, project.project_id, image_family, bucket)




# create storage client
def create_storage_client(project):
    # check if auth type is oauth
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return storage.Client(project=project.project_id, credentials=credentials)
    # create the storage client
    return storage.Client()




def __create_bucket(storage_client, bucket_name, location, key):
    """Creates a new bucket."""
    try:
        # check if bucket exists
        bucket = storage_client.get_bucket(bucket_name)
        logger.info(f"Bucket {bucket.name} exists.")
    except:
        logger.info(f"Bucket {bucket_name} does not exist.")
        # create the bucket
        storage_client.create_bucket(bucket_name, location=location)
        logger.info(f"Bucket {bucket_name} created.")
    
    # get the bucket
    bucket = storage_client.get_bucket(bucket_name)
    logger.info(f"Setting default encryption key for {bucket.name} bucket...")
    # check if the key is dict 
    if isinstance(key, str):
        key_name = key
    elif isinstance(key, dict):
        # get the key name
        key_name = key['name']
    else:
        key_name = key.name
    bucket.default_kms_key_name = key_name
    bucket.patch()
    logger.success(f"Default encryption key for {bucket.name} bucket set to {key_name}.")
    return bucket


def __list_buckets(storage_client):
    """Lists all buckets."""

    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)


def __delete_bucket(storage_client, bucket_name):
    """Deletes a bucket. The bucket must be empty."""
    # bucket_name = "your-bucket-name"

    bucket = storage_client.bucket(bucket_name)
    try:
        bucket.delete()
        print(f"Bucket {bucket.name} deleted.")
    except Exception as e:
        logger.error(f"Error deleting bucket {bucket_name} with error: {e}")
        raise e



def __upload_blob(storage_client, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    logger.info(f"Uploading {source_file_name} to {bucket_name} bucket...")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    
    logger.success(f"File {source_file_name} uploaded to {destination_blob_name}.") 
    # generate public link for the uploaded file
    return blob.public_url


def __download_blob(storage_client, bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def __list_blobs(storage_client, bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)


def __upload_startup_script(client, project_id: str, image_family: str, bucket, cluster_name: str, cluster_size: int, secret_name: str):
    """Uploads the selected startup script base on image family, to the created bucket if not existing and return the startup script url."""
    logger.info(f"Uploading startup script for {image_family} image family...")
    
    # Selecting startup script based on the OS family
    dist = image_family.split('-')[0]
    if dist == 'debian' or dist == 'ubuntu':
        startup_script = "startup-script-debian.sh"
        script_template = "startup-script-debian.j2"
    elif dist == 'rhel':
        startup_script = "startup-script-rhel.sh"
        script_template = "startup-script-rhel.j2"
    elif dist ==  'suse':
        startup_script = "startup-script-suse.sh"
        script_template = "startup-script-suse.j2"
    else:
        logger.error(f"Unsupported OS family: {dist}")
        raise GCPUnsupportedOSFamilyException(f"Unsupported OS family: {dist}")


    # read the template 
    with open(f"./shared/bin/startup-scripts/{script_template}", "r") as f:
        template = Template(f.read())


    nodes = [f"{cluster_name}-{instance_range:03d}" for instance_range in range(cluster_size)] 
    master_node_name = nodes[0]
    # map nodes list to hostnames list  using gcp internal dns
    hostnames = list(map(lambda node: node + ".c." + project_id + ".internal", nodes))
    # get the master node hostname
    master_node_hostname = hostnames[0]
    # remove the master node from the list 
    hostnames.pop(0)

    # render the template 
    rendered_template = template.render(master_node_name=master_node_name, master_node_hostname=master_node_hostname, nodes=hostnames, couchbase_secret_name=secret_name)
    # write the rendered template to a file
    with open(f"./shared/bin/startup-scripts/{startup_script}", "w") as f:
        f.write(rendered_template)

    # upload the startup script to the bucket
    startup_script_url = __upload_blob(client, bucket.name, os.path.abspath(f"shared/bin/startup-scripts/{startup_script}"), startup_script)

    return startup_script_url


# uploading shutdown scripts
def __upload_shutdown_script(client, project_id: str, image_family: str, bucket):
    """Uploads the shutdown script based on the image family"""
    logger.info(f"Uploading shutdown script for {image_family} image family...")

    # Selecting shutdown script based on the OS family
    dist = image_family.split('-')[0]

    if dist == 'debian' or dist == 'ubuntu':
        shutdown_script = "shutdown-script-debian.sh"
        script_template = "shutdown-script-debian.j2"
    elif dist == 'rhel':
        shutdown_script = "shutdown-script-rhel.sh"
        script_template = "shutdown-script-rhel.j2"
    elif dist ==  'suse':
        shutdown_script = "shutdown-script-suse.sh"
        script_template = "shutdown-script-suse.j2"
    else:
        logger.error(f"Unsupported OS family: {dist}")
        raise GCPUnsupportedOSFamilyException(f"Unsupported OS family: {dist}")
    # read the template 
    with open(f"./shared/bin/shutdown-scripts/{script_template}", "r") as f:
        template = Template(f.read())


    # render the template 
    rendered_template = template.render()
    # write the rendered template to a file
    with open(f"./shared/bin/shutdown-scripts/{shutdown_script}", "w") as f:
        f.write(rendered_template)


    # upload the startup script to the bucket
    shutdown_script_url = __upload_blob(client, bucket.name, os.path.abspath(f"shared/bin/shutdown-scripts/{shutdown_script}"), shutdown_script)

    return shutdown_script_url



