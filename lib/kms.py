from google.cloud import kms

def create_key_ring(project_id, location_id, key_ring_id):
    """
    Creates a new key ring in Cloud KMS
    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the key ring to create (e.g. 'my-key-ring').
    Returns:
        KeyRing: Cloud KMS key ring.
    """

    

    # Create the client.
    client = kms.KeyManagementServiceClient()

    # Build the parent location name.
    location_name = f'projects/{project_id}/locations/{location_id}'

    # Build the key ring.
    key_ring = {}

    # Call the API.
    created_key_ring = client.create_key_ring(
        request={'parent': location_name, 'key_ring_id': key_ring_id, 'key_ring': key_ring})
    print('Created key ring: {}'.format(created_key_ring.name))
    return created_key_ring


def create_key_symmetric_encrypt_decrypt(project_id, location_id, key_ring_id, key_id):
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

    # Import the client library.
    from google.cloud import kms

    # Create the client.
    client = kms.KeyManagementServiceClient()

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
    print('Created symmetric key: {}'.format(created_key.name))
    return created_key