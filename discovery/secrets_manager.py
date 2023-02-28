import os
import base64
import google_crc32c
from google.cloud import secretmanager
from loguru import logger
import google.oauth2.credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account







def setup_secret_manager(project, cluster, couchbase_params):
    """
    Setup the secret manager for the cluster
    Args:
        project: GCP project object
        cluster: cluster object
        couchbase_params: Couchbase params object
    """

    # admin password secret
    secret_name = f"{cluster.name}-admin-creds"
    # create service 
    secrets_manager_service = build_secrets_manager_service(project)
    # check if the params are not null
    if couchbase_params is  None:
        logger.info(f"Couchbase credentials not specified, we will check if the secret already exists")
        secret = __check_secret(secrets_manager_service, project.project_id, secret_name)
        if secret is None:
            logger.info("Couchbase secret don't exists ")
            exit(1)
        else:
            logger.info("Couchbase secret already exists")
            logger.info(f"The cluster will use the 'latest' version of secret {secret}")
    else:    
        logger.info(f"Couchbase credentials specified, we will check if the secret already exists")
        secret = __check_secret(secrets_manager_service, project.project_id, secret_name)
        if secret is None:
            logger.info("Creating secret manager for admin creds ...")
            secret = __create_secret(secrets_manager_service, project.project_id, secret_name)
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            __add_latest_secret_version(secrets_manager_service, project.project_id, secret_name, admin_creds)
        else:
            logger.info("Secret already exists, therefore we will update the 'latest' version")
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            __add_latest_secret_version(secrets_manager_service, project.project_id, secret_name, admin_creds)
    return secret_name











def build_secrets_manager_service(project): 
    # check if auth type is oauth 
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
    else:
        # get service account path 
        path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        # Build from the service account 
        credentials = service_account.Credentials.from_service_account_file(path)

    secrets_manager_service = build('secretmanager', 'v1beta1', credentials=credentials)
    return secrets_manager_service


    
def __assign_permissions_to_service_account(project, storage_params, region, key):

    logger.info("Assigning read secrets role to the compute service account...") 
    # Add Compute Engine default service account to the bucket
    # read member from environment variable
    member = {"user": os.environ['COMPUTE_ENGINE_SERVICE_ACCOUNT_EMAIL']}
    role = "roles/storage.objectViewer"

    policy = bucket.get_iam_policy(requested_policy_version=3)

    policy.bindings.append({"role": role, "members": [member]})

    bucket.set_iam_policy(policy)
    logger.debug(f"Added {member} to {bucket.name} with {role} role.")

    return bucket


# check if the secret exists
def __check_secret(service, project_id, secret_name):
    logger.info(f"Checking if {secret_name} exists...") 
    # use discovery api to check if the secret exists 
    name = f"projects/{project_id}/secrets/{secret_name}"
    try:
        response = service.projects().secrets().get(name=name).execute()
        logger.success(f"Secret {secret_name} exists.")
        return response
    except:
        logger.error(f"Secret {secret_name} doesn't exist.")
        return None


# create the secret
def __create_secret(service, project_id, secret_name):
    logger.info(f"Creating secret {secret_name}...")
    # Build the parent resource name
    # use the discovery api to create a secret with secret_name 
    name = f"projects/{project_id}"
    body = {
        "replication": {
            "automatic": {}
        }
    }
    try:
        response = service.projects().secrets().create(parent=name, secretId=secret_name, body=body).execute()
        # check the response 
        if response is None:
            logger.error(f"Secret {secret_name} creation failed.")
            exit(1)
        else:
            logger.success(f"Secret {secret_name} created successfully.")
    except Exception as e:
        logger.error(f"Secret {secret_name} creation failed.")
        logger.error(e)
        exit(1)



# add the secret version
def __add_latest_secret_version(service, project_id, secret_name, secret_value):
    
    # Create the secret payload
    payload = secret_value

    # caclculate the crc32c hash
    # crc32c = google_crc32c.Checksum()
    # crc32c.update(payload.encode('utf-8'))

    # use the discovery api to add a version to the secret 
    name = f"projects/{project_id}/secrets/{secret_name}"
    body = {
        "payload": {
            "data": base64.b64encode(payload.encode('utf-8')).decode('utf-8'),
        }
    }
    try:
        # addVersion 
        response = service.projects().secrets().addVersion(parent=name, body=body).execute()
        # print version 
        if response is None:
            logger.error(f"Secret {secret_name} version creation failed.")
            exit(1)
        else:
            logger.success(f"Secret {secret_name} version created successfully.")
            return response
    except Exception as e:
        logger.error(f"Secret {secret_name} version creation failed.")
        logger.error(e)
        exit(1)

