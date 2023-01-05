#!/bin/bash
# Init a couchbase cluster 

# Create the cluster
/opt/couchbase/bin/couchbase-cli cluster-init -c 10.200.15.210:8091 --cluster-username=admin --cluster-password=password 


  # Add nodes
  /opt/couchbase/bin/couchbase-cli server-add -c 10.200.15.210:8091 --server-add=10.200.15.209:8091 --server-add-username=admin --server-add-password=password --username=admin --password=password


# Rebalance
/opt/couchbase/bin/couchbase-cli rebalance -c 10.200.15.210:8091 -u admin -p password