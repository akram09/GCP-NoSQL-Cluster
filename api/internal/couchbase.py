from datetime import timedelta
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator, CertificateAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
import os 
from loguru import logger


class CouchbaseCluster():
    # init method or constructor
    def __init__(self):
        self.cluster = None 

    def init_couchbase(self):
        # check if the environment variable is set
        if os.environ.get('COUCHBASE_HOST') is not None:
            logger.info('COUCHBASE_HOST is set')
            # get the environment variable
            host = os.environ.get('COUCHBASE_HOST')
        else:
            logger.info('COUCHBASE_HOST is not set')
            logger.info('Setting default host to localhost')
            # set the default host
            host = 'localhost'

        logger.info("Checking authentication method")
        # check if the certificate path is set 
        if os.environ.get('COUCHBASE_CERT_PATH') is not None:
            # get the certificate path
            cert_path = os.environ.get('COUCHBASE_CERT_PATH')
            # create authenticator 
            authenticator = CertificateAuthenticator(cert_path)
            # create cluster options
            options = ClusterOptions(authenticator)
            # create cluster object
            self.cluster = Cluster('couchbase://' + host, options)
        else:
            # check if password and username are set 
            if os.environ.get('COUCHBASE_USER') is not None and os.environ.get('COUCHBASE_PASSWORD') is not None:
                # get the username and password
                username = os.environ.get('COUCHBASE_USER')
                password = os.environ.get('COUCHBASE_PASSWORD')
                # create PasswordAuthenticator
                authenticator = PasswordAuthenticator(username, password)
                # create cluster options
                options = ClusterOptions(authenticator)
                # create cluster object
                self.cluster = Cluster('couchbase://' + host, options)
            else:
                logger.error('COUCHBASE_USER and COUCHBASE_PASSWORD are not set')
                logger.error('COUCHBASE_CERT_PATH is not set')
                logger.error('Exiting')
                exit(1)
        # Wait until the cluster is ready for use.
        self.cluster.wait_until_ready(timedelta(seconds=5))
    def insert(self, bucket, key, value):
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # insert the document
        collection.upsert(key, value)
        # return the document
        document = collection.get(key)
        return document.content_as[dict]
    
    def get(self, bucket, key):
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # return the document
        document = collection.get(key)

        return document.content_as[dict]
