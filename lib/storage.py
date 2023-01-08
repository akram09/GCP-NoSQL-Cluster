from loguru import logger
from google.cloud import storage
import os
from jinja2 import Template

def create_bucket(bucket_name):
    """Creates a new bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        bucket = storage_client.create_bucket(bucket_name)
        logger.info(f"Bucket {bucket.name} created.")
    else:
        logger.info(f"Bucket {bucket.name} exists.")
    return bucket


def list_buckets():
    """Lists all buckets."""
    storage_client = storage.Client()

    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)


def delete_bucket(bucket_name):
    """Deletes a bucket. The bucket must be empty."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.delete()

    print(f"Bucket {bucket.name} deleted.")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    logger.info(f"Uploading {source_file_name} to {bucket_name} bucket...")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    
    logger.success(f"File {source_file_name} uploaded to {destination_blob_name}.") 
    # generate public link for the uploaded file
    return blob.public_url


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)


def upload_startup_script(image_family: str, bucket_name: str):
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
        raise("There is no startup script for the selected OS family.")

    logger.info("Checking if the bucket exists else creating the bucket...")
    # Create the bucket if not existed
    bucket = create_bucket(bucket_name)

    logger.info("Assigning read storage role to the bucket...") 
    # Add Compute Engine default service account to the bucket
    # read member from environment variable
    member = {"user": os.environ['COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL']}
    role = "roles/storage.objectViewer"

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": [member]})

    bucket.set_iam_policy(policy)
    logger.debug(f"Added {member} to {bucket.name} with {role} role.")

    # read the template 
    with open(f"./bin/couchbase-install/{script_template}", "r") as f:
        template = Template(f.read())
    # render the template 
    rendered_template = template.render(bucket_name=bucket_name)
    # write the rendered template to a file
    with open(f"./bin/couchbase-install/{startup_script}", "w") as f:
        f.write(rendered_template)

    # upload the startup script to the bucket
    startup_script_url = upload_blob(bucket.name, os.path.abspath(f"bin/couchbase-install/{startup_script}"), startup_script)

    return startup_script_url

# render the cluster provisioning script and upload it to the bucket 
def upload_cluster_provisioning_script(bucket_name: str): 
    cluster_provisioning_script = "cluster-init.sh"
    script_template = "cluster-init.j2"

    # read the template 
    with open(f"./bin/cluster-provisioning/{script_template}", "r") as f:
        template = Template(f.read())
    # render the template 
    rendered_template = template.render()
    # write the rendered template to a file
    with open(f"./bin/cluster-provisioning/{cluster_provisioning_script}", "w") as f:
        f.write(rendered_template)

    # upload the startup script to the bucket
    cluster_provisioning_script_url = upload_blob(bucket_name, os.path.abspath(f"bin/cluster-provisioning/{cluster_provisioning_script}"), cluster_provisioning_script)

    return cluster_provisioning_script_url
