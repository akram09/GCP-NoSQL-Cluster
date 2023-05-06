# Description: This file contains functions to create and manage encryption keys in Google Cloud KMS
import os 
import uuid
from loguru import logger
from google.cloud import kms
import google.oauth2.credentials
from utils.exceptions import GCPKMSKeyCreationFailedException, GCPKMSKeyRingCreationFailedException, GCPKMSKeyPermissionAssignmentFailedException






def setup_encryption_keys(project, cluster_name, region):
    """
    Setup encryption keys for the cluster. This involves creating a key ring and a symmetric encryption/decryption key .
    """

    # create secret manager client
    client = create_key_management_service_client(project)

    # Create KMS key ring and symmetric encryption/decryption key
    key_ring_id = f"key-ring-{cluster_name}" 
    logger.info(f"Checking key ring {key_ring_id} ...")
    # check if key ring exists 
    key_ring = __get_key_ring(client, project.project_id, region, key_ring_id)
    if key_ring is None: 
        logger.debug("Key ring does not exist, creating key ring")
        key_ring = __create_key_ring(client, project.project_id, region, key_ring_id)

    logger.info("Checking encryption key ...")
    key_id = f"key-{cluster_name}"
    key = __create_key_symmetric_encrypt_decrypt(client, project.project_id, region, key_ring_id, key_id+f"-{uuid.uuid4().hex}")
    return key






# public function 
def create_key_ring(project, location_id, key_ring_id):
    client = create_key_management_service_client(project)
    return __create_key_ring(client, project.project_id, location_id, key_ring_id)


# public function
def get_key_ring(project, location_id, key_ring_id):
    client = create_key_management_service_client(project)
    return __get_key_ring(client, project.project_id, location_id, key_ring_id)

# public function   
def create_key_symmetric_encrypt_decrypt(project, location_id, key_ring_id, key_id):
    client = create_key_management_service_client(project)
    return __create_key_symmetric_encrypt_decrypt(client, project.project_id, location_id, key_ring_id, key_id)

# public function
def assign_permission_to_storage(project, location_id, key_ring_id, key_id, bucket_name):
    client = create_key_management_service_client(project)
    return __assign_permission_to_storage(client, project.project_id, location_id, key_ring_id, key_id, bucket_name)

# public function
def get_key_symmetric_encrypt_decrypt(project, location_id, key_ring_id, key_id):
    client = create_key_management_service_client(project)
    return __get_key_symmetric_encrypt_decrypt(client, project.project_id, location_id, key_ring_id, key_id)

# create keyManagementServiceClient
def create_key_management_service_client(project): 
    # check if auth type is oauth  
    if project.auth_type == "oauth":
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        return kms.KeyManagementServiceClient(credentials=credentials)
    # create the secret manager client
    return kms.KeyManagementServiceClient()

def __create_key_ring(client, project_id, location_id, key_ring_id):
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

    # Build the parent location name.
    location_name = f'projects/{project_id}/locations/{location_id}'

    # Build the key ring.
    key_ring = {}
    try:
        # Call the API.
        created_key_ring = client.create_key_ring(
            request={'parent': location_name, 'key_ring_id': key_ring_id, 'key_ring': key_ring})
        logger.success(f"Created key ring {created_key_ring.name}")
        return created_key_ring
    except Exception as e:
        logger.error(f"Error creating key ring {key_ring_id} in project {project_id}")
        logger.error(e)
        raise GCPKMSKeyRingCreationFailedException(f"Error creating key ring {key_ring_id} in project {project_id}")


# get key ring 
def __get_key_ring(client, project_id, location_id, key_ring_id):
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

    # Build the key ring name
    key_ring_name = client.key_ring_path(project_id, location_id, key_ring_id)

    # Call the API
    try:
        key_ring = client.get_key_ring(name=key_ring_name)
        logger.success(f"Got key ring {key_ring.name}")
        return key_ring
    except Exception as e:
        logger.error(f"Error getting key ring {key_ring_id} in project {project_id}")
        return None



def __create_key_symmetric_encrypt_decrypt(client, project_id, location_id, key_ring_id, key_id):
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

    # Build the parent key ring name.
    key_ring_name = client.key_ring_path(project_id, location_id, key_ring_id)

    # Build the key.
    purpose = kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
    algorithm = kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.GOOGLE_SYMMETRIC_ENCRYPTION
    key = {
        'purpose': purpose,
        'version_template': {
            'algorithm': algorithm,
        }
    }
    
    try:
        # Call the API.
        created_key = client.create_crypto_key(
            request={'parent': key_ring_name, 'crypto_key_id': key_id, 'crypto_key': key})
        __assign_permission_to_storage(client, project_id, key_ring_id, key_id, location_id)
        return created_key
    except Exception as e:
        logger.error(f"Error creating key {key_id} in key ring {key_ring_id} in project {project_id}")
        logger.error(e)
        raise GCPKMSKeyCreationFailedException(f"Error creating key {key_id} in key ring {key_ring_id} in project {project_id}")



def __assign_permission_to_storage(client, project_id, key_ring_id, key_id, location):
    logger.info(f"Assigning permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
    key_name = client.crypto_key_path(project_id, location, key_ring_id, key_id)

    # Build the policy
    policy = client.get_iam_policy(request={'resource': key_name})


    # get cloud storage service account from env 
    service_account = os.environ.get('CLOUD_STORAGE_SERVICE_ACCOUNT_EMAIL')

    policy.bindings.add(
        role='roles/cloudkms.cryptoKeyEncrypterDecrypter',
        members=[f'serviceAccount:{service_account}']
    )
    try:
        # Call the API.
        updated_policy = client.set_iam_policy(request={'resource': key_name, 'policy': policy})
    except Exception as e:
        logger.error(f"Error assigning permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
        logger.error(e)
        raise GCPKMSKeyPermissionAssignmentFailedException(f"Error assigning permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")
    logger.success(f"Assigned permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")



# get key by key ring id and key id 
def __get_key_symmetric_encrypt_decrypt(client, project_id, location_id, key_ring_id, key_id):
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

    # Build the key name.
    key_name = client.crypto_key_path(project_id, location_id, key_ring_id, key_id)

    # Call the API.
    try:
        key = client.get_crypto_key(name=key_name)
        logger.success(f"Got key {key.name}")
        return key
    except Exception as e:
        logger.error(f"Error getting key {key_id} in key ring {key_ring_id} in project {project_id}")
        return None


def is_key_enabled(key):
    # check if the key is enabled 
    return key.primary.state == kms.CryptoKeyVersion.CryptoKeyVersionState.ENABLED
