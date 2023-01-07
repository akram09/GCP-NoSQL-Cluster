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

# Wait 3 minutes for couchbase server to start
sleep 180

# Pull the cluster init script from gcp bucket 
gsutil cp gs://bucket-7972cfbe-3da3-4f7f-a1fa-770a13c853eb/cluster-provisioning/cluster-init.sh .

# Change the permission of the script
chmod +x cluster-init.sh

# Run the script
./cluster-init.sh