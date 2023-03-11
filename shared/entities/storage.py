
class GCPStorageParams:
    def __init__(self, bucket, type="gcp_storage"):
        self.bucket = bucket
        self.type = type
    
    def __str__(self):
        return f"StorageParams(bucket={self.bucket}, type={self.type})"
