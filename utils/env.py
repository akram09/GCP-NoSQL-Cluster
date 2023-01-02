import os 

# check environment variables 
def check_env():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise Exception("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    if "GOOGLE_CLOUD_PROJECT" not in os.environ:
        raise Exception("Please set GOOGLE_CLOUD_PROJECT environment variable")
    if "GOOGLE_CLOUD_ZONE" not in os.environ:
        raise Exception("Please set GOOGLE_CLOUD_ZONE environment variable")

    
