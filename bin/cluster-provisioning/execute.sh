#!/bin/bash
# This script use gcloud to create a cluster of couchbase server

# Authenticate gcloud with the service account 
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# Set the project
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Set the zone
gcloud config set compute/zone $GOOGLE_CLOUD_ZONE

# Create the cluster
gcloud compute ssh --zone $GOOGLE_CLOUD_ZONE $MASTER_NODE_NAME --command "bash -s" < bin/cluster-provisioning/start.sh
