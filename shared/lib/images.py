import google.oauth2.credentials
from loguru import logger
from google.cloud import compute_v1
from utils.exceptions import GCPImageNotFoundException



    

# public function
def get_image_from_family(project, image_project, family):
    client = create_images_client(project)
    return __get_image_from_family(client, image_project, family)
    

def create_images_client(project): 
    # check if auth type is oauth  
    if project.auth_type == "oauth": 
        # get the service token
        service_token = project.service_token
        # create auth credentials
        credentials = google.oauth2.credentials.Credentials(token=service_token)
        client = compute_v1.ImagesClient(credentials=credentials)
        return client
    return compute_v1.ImagesClient()


# private function that abstracts the gcp client creation
def __get_image_from_family(client, image_project, family: str) -> compute_v1.Image:
    """
    Retrieve the newest image that is part of a given family in a project.
    Args:
        project: project ID or project number of the Cloud project you want to get image from.
        family: name of the image family you want to get image from.
    Returns:
        An Image object.
    """
    logger.info(f"Getting image from family {family} in project {image_project}")
    # List of public operating system (OS) images: https://cloud.google.com/compute/docs/images/os-details
    try:

        newest_image = client.get_from_family(project=image_project, family=family)
        return newest_image
    except Exception as e:
        logger.error(f"Error getting image from family {family}: {e}")
        raise GCPImageNotFoundException(f"Error getting image from family {family}: {e}")
