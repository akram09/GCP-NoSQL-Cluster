from google.cloud import storage
import os

def create_bucket(bucket_name):
    """Creates a new bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        bucket = storage_client.create_bucket(bucket_name)
        print(f"Bucket {bucket.name} created.")
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

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    
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
    
    # Selecting startup script based on the OS family
    dist = image_family.split('-')[0]
    if dist == 'debian' or dist == 'ubuntu':
        startup_script = "startup-script-debian.sh"
    elif dist == 'rhel':
        startup_script = "startup-script-rhel.sh"
    elif dist ==  'suse':
        startup_script = "startup-script-suse.sh"
    else:
        raise("There is no startup script for the selected OS family.")

    # Create the bucket if not existed
    bucket = create_bucket(bucket_name)
    
    # upload the startup script to the bucket
    startup_script_url = upload_blob(bucket.name, os.path.abspath(f"bin/{startup_script}"), startup_script)

    return startup_script_url