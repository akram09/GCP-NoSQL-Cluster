import os 
import uuid
from loguru import logger
from google.cloud import kms
import google.oauth2.credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account






def setup_encryption_keys(project, cluster_name, region):

    # build the kms service 
    kms_service = create_key_management_service(project)
    # Create KMS key ring and symmetric encryption/decryption key
    key_ring_id = f"key-ring-{cluster_name}" 
    logger.info(f"Checking key ring {key_ring_id} ...")
    # check if key ring exists 
    key_ring = __get_key_ring(kms_service, project.project_id, region, key_ring_id)
    if key_ring is None: 
        logger.debug("Key ring does not exist, creating key ring")
        key_ring = __create_key_ring(kms_service, project.project_id, region, key_ring_id)

    logger.info("Checking encryption key ...")
    key_id = f"key-{cluster_name}"
    key = __create_key_symmetric_encrypt_decrypt(kms_service, project.project_id, region, key_ring_id, key_id+f"-{uuid.uuid4().hex}")
    return key




# create keyManagementServiceClient
def create_key_management_service(project): 
    # check if auth type is oauth  
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
    else:
        # get service account path
        service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        # create credentials
        credentials = service_account.Credentials.from_service_account_file(service_account_path)
    # build the service 
    kms_service = build('cloudkms', 'v1', credentials=credentials)
    return kms_service



def __create_key_ring(service, project_id, location_id, key_ring_id):
    """
    Creates a new key ring in Cloud KMS
    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the key ring to create (e.g. 'my-key-ring').
    Returns:
        KeyRing: Cloud KMS key ring.
    """
    logger.info(f"Creating key ring {key_ring_id}  in project {project_id}")
    try:
        # use the discovery api to create a key ring 
        key_ring = service.projects().locations().keyRings().create(
            parent=f"projects/{project_id}/locations/{location_id}",
            keyRingId=key_ring_id
        ).execute()
        # check 
        if key_ring is None:
            logger.error(f"Error creating key ring {key_ring_id} in project {project_id}")
            return None
        # log success
        logger.success(f"Created key ring {key_ring_id} in project {project_id}")
        # return the key ring
        return key_ring
    except Exception as e:
        logger.error(f"Error creating key ring {key_ring_id} in project {project_id}")
        logger.error(e)
        exit(1)


# get key ring 
def __get_key_ring(service, project_id, location_id, key_ring_id):
    """
    Gets a key ring from Cloud KMS.
    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
    Returns:
        KeyRing: Cloud KMS key
    """
    logger.info(f"Getting key ring {key_ring_id} in project {project_id}")
    # use the discovery api to get the key ring
    try:
        key_ring = service.projects().locations().keyRings().get(
            name=f"projects/{project_id}/locations/{location_id}/keyRings/{key_ring_id}"
        ).execute() 
        logger.success(f"Got key ring {key_ring_id} in project {project_id}")
        return key_ring
    except Exception as e:
        logger.error(f"Error getting key ring {key_ring_id} in project {project_id}")
        return None


def __create_key_symmetric_encrypt_decrypt(service, project_id, location_id, key_ring_id, key_id):
    """
    Creates a new symmetric encryption/decryption key in Cloud KMS.
    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
        key_id (string): ID of the key to create (e.g. 'my-symmetric-key').
    Returns:
        CryptoKey: Cloud KMS key.
    """
    try:
        # use the discovery api to create a key
        key = service.projects().locations().keyRings().cryptoKeys().create(
            parent=f"projects/{project_id}/locations/{location_id}/keyRings/{key_ring_id}",
            body={ "purpose": "ENCRYPT_DECRYPT", "versionTemplate": {"algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION"}},
            cryptoKeyId=key_id
        ).execute()
        # check
        if key is None:
            logger.error(f"Error creating key {key_id} in key ring {key_ring_id} in project {project_id}")
            return None
        # log success
        logger.success(f"Created key {key_id} in key ring {key_ring_id} in project {project_id}")
        __assign_permission_to_storage(service, project_id, key_ring_id, key_id, location_id)
        return key
    except Exception as e:
        logger.error(f"Error creating key {key_id} in key ring {key_ring_id} in project {project_id}")
        logger.error(e)
        exit(1)


def __assign_permission_to_storage(service, project_id, key_ring_id, key_id, location):
    logger.info(f"Assigning permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
    # use the discovery api to assign permissions to the service account 
    policy = service.projects().locations().keyRings().getIamPolicy(
        resource=f"projects/{project_id}/locations/{location}/keyRings/{key_ring_id}"
    ).execute()
    # get cloud storage service account from env
    service_account = os.environ.get('CLOUD_STORAGE_SERVICE_ACCOUNT_EMAIL')
    # add the service account to the policy
    # check bindings exist
    if 'bindings' not in policy:
        policy['bindings'] = []

    policy['bindings'].append({
        "role": "roles/cloudkms.cryptoKeyEncrypterDecrypter",
        "members": [f"serviceAccount:{service_account}"]
    })
    # update the policy
    updated_policy = service.projects().locations().keyRings().setIamPolicy(
        resource=f"projects/{project_id}/locations/{location}/keyRings/{key_ring_id}",
        body={"policy": policy}
    ).execute()
    # check
    if updated_policy is None:
        logger.error(f"Error assigning permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
        return None
    # log success
    logger.success(f"Assigned permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
    return updated_policy


# get key by key ring id and key id 
def __get_key_symmetric_encrypt_decrypt(service, project_id, location_id, key_ring_id, key_id):
    """
    Gets a symmetric encryption/decryption key from Cloud KMS.
    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
        key_id (string): ID of the key to get (e.g. 'my-symmetric-key').
    Returns:
        CryptoKey: Cloud KMS key.
    """
    logger.info(f"Getting key {key_id} in key ring {key_ring_id} in project {project_id}")
    # use the discovery api to get the key
    key = service.projects().locations().keyRings().cryptoKeys().get(
        name=f"projects/{project_id}/locations/{location_id}/keyRings/{key_ring_id}/cryptoKeys/{key_id}"
    ).execute()
    # check
    if key is None:
        logger.error(f"Error getting key {key_id} in key ring {key_ring_id} in project {project_id}")
        return None
    # log success
    logger.success(f"Got key {key_id} in key ring {key_ring_id} in project {project_id}")
    return key



def is_key_enabled(key):
    # check if the key is enabled 
    return key.primary.state == kms.CryptoKeyVersion.CryptoKeyVersionState.ENABLED
