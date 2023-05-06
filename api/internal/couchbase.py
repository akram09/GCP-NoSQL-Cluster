# Description: This module contains the CouchbaseCluster class which is an abstraction on top of the Couchbase Python SDK. This allows us to easily switch to another database in the future. The CouchbaseCluster class is used to connect to the Couchbase cluster and perform operations on the cluster.
from datetime import timedelta
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator, CertificateAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.management.options import CreatePrimaryQueryIndexOptions
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
        """
        Insert a document into the database
        Parameters:
            bucket (str): The name of the bucket
            key (str): The key of the document
            value (dict): The value of the document
        Returns:
            dict: The document that was inserted
        """
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # insert the document
        collection.upsert(key, value)
        # return the document
        document = collection.get(key)
        return document.content_as[dict]

    def update(self, bucket, key, value):
        """
        Update a document in the database
        """
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # update the document
        collection.replace(key, value)
        # return the document
        document = collection.get(key)
        return document.content_as[dict]
    
    def get(self, bucket, key):
        """
        Get a document from the database
        Parameters:
            bucket (str): The name of the bucket
            key (str): The key of the document
        Returns:
            dict: The document that was retrieved
        """
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # return the document
        document = collection.get(key)

        return document.content_as[dict]

    def check(self, bucket, key):
        """
        Check if a document exists in the database
        """
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()
        # return the document
        document = collection.get(key)

        return document.success
    
    def list(self, bucket):
        """
        List the documents of a bucket.
        """
        # get the bucket
        bucket = self.cluster.bucket(bucket)
        # get the collection
        collection = bucket.default_collection()

        # create primary index and ignore if it exists
        view_manager = bucket.view_indexes()
        query_index_manager = self.cluster.query_indexes()
        query_index_manager.create_primary_index(bucket.name, CreatePrimaryQueryIndexOptions(ignore_if_exists=True))

        # create query options
        options = QueryOptions()
        # create query
        query = 'SELECT * FROM `' + bucket.name + '`'
        # execute query
        result = self.cluster.query(query, options)
        # return the result
        return result.rows()
