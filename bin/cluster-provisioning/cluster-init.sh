#!/bin/bash
# Init a couchbase cluster 


# check if we are in the master node based on the hostname -a  
# if we are in the master node, we will init the cluster
if [[ $(hostname -a) ==  ]]; then
    echo "Init the cluster" 
    /opt/couchbase/bin/couchbase-cli cluster-init -c :8091 --cluster-username= --cluster-password= 
    
    # add the other nodes to the cluster

    
    # Rebalance
    /opt/couchbase/bin/couchbase-cli rebalance -c :8091 -u  -p 
fi