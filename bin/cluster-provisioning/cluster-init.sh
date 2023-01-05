#!/bin/bash
# Init a couchbase cluster 

# Create the cluster
/opt/couchbase/bin/couchbase-cli cluster-init -c 10.200.15.211:8091 --cluster-username=m0kr4n3 --cluster-password=password 


  # Add nodes
  /opt/couchbase/bin/couchbase-cli server-add -c 10.200.15.211:8091 --server-add=10.200.15.212:8091 --server-add-username=m0kr4n3 --server-add-password=password --username=m0kr4n3 --password=password


# Rebalance
/opt/couchbase/bin/couchbase-cli rebalance -c 10.200.15.211:8091 -u m0kr4n3 -p password