import os
import google_crc32c
from google.cloud import secretmanager
from loguru import logger
import google.oauth2.credentials


# create secret Manager Service Client 
def create_secret_manager_client(project):
    # check if auth type is oauth 
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return secretmanager.SecretManagerServiceClient(credentials=credentials)
    # create the secret manager client
    client = secretmanager.SecretManagerServiceClient()
    return client
    


# check if the secret exists
def check_secret(client, project_id, secret_name):
    logger.info(f"Checking if {secret_name} exists...") 
    # get the secret name
    name = client.secret_path(project_id, secret_name)
    # try to get the secret
    try:
        response = client.get_secret(name=name)
        logger.success(f"Secret {secret_name} exists.")
        return response
    except:
        logger.error(f"Secret {secret_name} doesn't exist.")
        return None


# create the secret
def create_secret(client, project_id, secret_name):
    logger.info(f"Creating secret {secret_name}...")
    # Build the parent resource name
    parent = f"projects/{project_id}"

    # Create the secret payload
    response = client.create_secret(
        request={"parent": parent, "secret_id": secret_name, "secret": {"replication": {"automatic": {}},},}
    )
    logger.success(f"Secret {secret_name} created successfully.")


# add the secret version
def add_latest_secret_version(client, project_id, secret_name, secret_value):

    # Build the resource name
    parent = client.secret_path(project_id, secret_name)

    # Create the secret payload
    payload = secret_value.encode("UTF-8")

    # caclculate the crc32c hash
    crc32c = google_crc32c.Checksum()
    crc32c.update(payload)

    # Add the secret version
    response = client.add_secret_version(request={"parent": parent, "payload": {"data": payload, "data_crc32c": int(crc32c.hexdigest(), 16) }})

    # print version 
    logger.info(f"Secret version {response.name} added successfully.")

