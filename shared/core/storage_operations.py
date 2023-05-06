# Description: This file contains the functions to create and delete buckets in GCP
from loguru import logger
from shared.lib.storage import create_bucket, delete_bucket


def create_gcp_bucket(gcp_project, bucket_params):
    """
    Create a bucket with the given parameters.
    """
    bucket = create_bucket(gcp_project, bucket_params['name'], bucket_params['location'], bucket_params['key_name'])
    return bucket


def delete_gcp_bucket(gcp_project, bucket_params):
    """
    Delete a bucket with the given parameters.
    """
    bucket = delete_bucket(gcp_project, bucket_params['name'])
    return bucket
