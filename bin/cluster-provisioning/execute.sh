#!/bin/bash
# This script use gcloud to create a cluster of couchbase server


CLOUDSDK_PYTHON=$(which python)
export CLOUDSDK_PYTHON


# Get master node name from params 
MASTER_NODE_NAME=$1
echo "Master node name: $MASTER_NODE_NAME"

# Authenticate gcloud with the service account 
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Set the zone
gcloud config set compute/zone $GOOGLE_CLOUD_ZONE

# Create the cluster
gcloud compute ssh --project $GOOGLE_CLOUD_PROJECT --zone $GOOGLE_CLOUD_ZONE $MASTER_NODE_NAME --command "bash -s" < $PWD/bin/cluster-provisioning/cluster-init.sh
