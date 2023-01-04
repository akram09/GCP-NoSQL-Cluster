#!/bin/bash
# This script install couchbase server on debien to create a cluster of couchbase server

# Check the script is run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi


# Download the meta package 
curl -O https://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0-amd64.deb

# Install the meta package
dpkg -i couchbase-release-1.0-amd64.deb

# Update the package list
apt-get update

# Install couchbase server
apt-get install couchbase-server-community

# Start couchbase server
systemctl start couchbase-server-community


# remove the meta package
rm couchbase-release-1.0-amd64.deb


