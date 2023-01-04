#!/bin/bash
# Init a couchbase cluster 

# Create the cluster
couchbase-cli cluster-init -c localhost:8091 --cluster-username=$COUCHBASE_USER --cluster-password=$COUCHBASE_PASSWORD 


