import os 
from loguru import logger
from google.cloud import kms
import google.oauth2.credentials

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

def create_key_ring(client, project_id, location_id, key_ring_id):
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

    # Call the API.
    created_key_ring = client.create_key_ring(
        request={'parent': location_name, 'key_ring_id': key_ring_id, 'key_ring': key_ring})
    logger.success(f"Created key ring {created_key_ring.name}")
    return created_key_ring


# get key ring 
def get_key_ring(client, project_id, location_id, key_ring_id):
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



def create_key_symmetric_encrypt_decrypt(client, project_id, location_id, key_ring_id, key_id):
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

    # Call the API.
    created_key = client.create_crypto_key(
        request={'parent': key_ring_name, 'crypto_key_id': key_id, 'crypto_key': key})
    assign_permission_to_storage(client, project_id, key_ring_id, key_id, location_id)
    return created_key


def assign_permission_to_storage(client, project_id, key_ring_id, key_id, location):
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

    # Call the API.
    updated_policy = client.set_iam_policy(request={'resource': key_name, 'policy': policy})
    logger.success(f"Assigned permission to storage for key {key_id} in key ring {key_ring_id} in project {project_id}")



# get key by key ring id and key id 
def get_key_symmetric_encrypt_decrypt(client, project_id, location_id, key_ring_id, key_id):
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
