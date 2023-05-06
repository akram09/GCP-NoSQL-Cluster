from loguru import logger
from shared.lib.kms import create_key_ring, create_key_symmetric_encrypt_decrypt



def key_ring_create(gcp_project, key_ring_params):
    """
    Create a key ring with the given parameters.
    """
    key_ring = create_key_ring(gcp_project, key_ring_params['location'], key_ring_params['name'])
    return key_ring

def key_create(gcp_project, key_params):
    """
    Create a key with the given parameters.
    """
    key = create_key_symmetric_encrypt_decrypt(gcp_project, key_params['location'], key_params['key_ring'], key_params['name'])
    return key
