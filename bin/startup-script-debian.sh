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

