#!/bin/bash
# This script install couchbase server on debien to create a cluster of couchbase server

# Download the meta package 
curl -O https://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0-amd64.deb

# Install the meta package
sudo dpkg -i couchbase-release-1.0-amd64.deb

# Update the package list
sudo apt-get update

# Install couchbase server
sudo apt-get install -y couchbase-server-community


# remove the meta package
rm couchbase-release-1.0-amd64.deb

# Init a couchbase cluster 


# check if we are in the master node based on the hostname -a  
# if we are in the master node, we will init the cluster
if [[ $(hostname -a) == mig-7-000 ]]; then
    echo "Init the cluster" 
    /opt/couchbase/bin/couchbase-cli cluster-init -c mig-7-000.c.upwork-python-automation.internal:8091 --cluster-username=kero --cluster-password=password 
    
    # add the other nodes to the cluster

    
      # Add nodes
    /opt/couchbase/bin/couchbase-cli server-add -c mig-7-000.c.upwork-python-automation.internal:8091 --server-add=mig-7-001.c.upwork-python-automation.internal:8091 --server-add-username=kero --server-add-password=password --username=kero --password=password

    
    # Rebalance
    /opt/couchbase/bin/couchbase-cli rebalance -c mig-7-000.c.upwork-python-automation.internal:8091 -u kero -p password
else
    # wait for the master node to init the cluster
    sleep 60
    # get node hostname
    node_hostname=$(hostname -a)
    echo "Join the cluster"
    # Join the cluster
    /opt/couchbase/bin/couchbase-cli server-add -c mig-7-000.c.upwork-python-automation.internal:8091 --server-add=$node_hostname:8091 --server-add-username=kero --server-add-password=password --username=kero --password=password
    # Rebalance
    /opt/couchbase/bin/couchbase-cli rebalance -c mig-7-000.c.upwork-python-automation.internal:8091 -u kero -p password
fi