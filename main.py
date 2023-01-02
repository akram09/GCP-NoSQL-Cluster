from google.cloud import storage
from .config import PROJECT_ID


def list_storage_buckets(project_id="your-google-cloud-project-id"):
    storage_client = storage.Client(project=project_id)
    buckets = storage_client.list_buckets()
    print("Buckets:")
    for bucket in buckets:
        print(bucket.name)
    print("Listed all storage buckets.")

if __name__ == "__main__":
    list_storage_buckets(project_id=PROJECT_ID)