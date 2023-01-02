from google.cloud import storage
from config import PROJECT_ID
from typing import Iterable
from google.cloud import compute_v1

def list_instances(project_id: str, zone: str) -> Iterable[compute_v1.Instance]:
    """
    List all instances in the given zone in the specified project.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone you want to use. For example: “us-west3-b”
    Returns:
        An iterable collection of Instance objects.
    """
    instance_client = compute_v1.InstancesClient()
    instance_list = instance_client.list(project=project_id, zone=zone)

    print(f"Instances found in zone {zone}:")
    for instance in instance_list:
        print(f" - {instance.name} ({instance.machine_type})")

    return instance_list

def list_storage_buckets(project_id="your-google-cloud-project-id"):
    storage_client = storage.Client(project=project_id)
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        print(bucket.name)
    print("Listed all storage buckets.")

if __name__ == "__main__":
    list_instances(PROJECT_ID, "us-west3-b")