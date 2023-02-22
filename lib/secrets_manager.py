import os
import google_crc32c
from google.cloud import secretmanager
from loguru import logger
import google.oauth2.credentials







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
    # create secret manager client
    client = create_secret_manager_client(project)

    # check if the params are not null
    if couchbase_params is  None:
        logger.info(f"Couchbase credentials not specified, we will check if the secret already exists")
        secret = __check_secret(client, project.project_id, secret_name)
        if secret is None:
            logger.info("Couchbase secret don't exists ")
            exit(1)
        else:
            logger.info("Couchbase secret already exists")
            logger.info(f"The cluster will use the 'latest' version of secret {secret}")
    else:    
        logger.info(f"Couchbase credentials specified, we will check if the secret already exists")
        secret = __check_secret(client, project.project_id, secret_name)
        if secret is None:
            logger.info("Creating secret manager for admin creds ...")
            secret = __create_secret(client, project.project_id, secret_name)
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            __add_latest_secret_version(client, project.project_id, secret_name, admin_creds)
        else:
            logger.info("Secret already exists, therefore we will update the 'latest' version")
            logger.info("Adding secret version for admin password ...")
            admin_creds = f"{couchbase_params.username}:{couchbase_params.password}"
            __add_latest_secret_version(client, project.project_id, secret_name, admin_creds)
    return secret_name






# public function 
def check_secret(project, secret_name):
    client = create_secret_manager_client(project)
    return __check_secret(client, project.project_id, secret_name)

# public function 
def add_latest_secret_version(project, secret_name, secret_value):
    client = create_secret_manager_client(project)
    return __add_latest_secret_version(client, project.project_id, secret_name, secret_value)




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
def __check_secret(client, project_id, secret_name):
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
def __create_secret(client, project_id, secret_name):
    logger.info(f"Creating secret {secret_name}...")
    # Build the parent resource name
    parent = f"projects/{project_id}"

    # Create the secret payload
    response = client.create_secret(
        request={"parent": parent, "secret_id": secret_name, "secret": {"replication": {"automatic": {}},},}
    )
    logger.success(f"Secret {secret_name} created successfully.")


# add the secret version
def __add_latest_secret_version(client, project_id, secret_name, secret_value):

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

