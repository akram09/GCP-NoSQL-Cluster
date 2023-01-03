#!/bin/bash
# This script join a couchbase cluster

# Join the cluster 
couchbase-cli server-add -c $MASTER_NODE_IP:8091 --server-add=$NODE_IP:8091 --server-add-username=$COUCHBASE_USER --server-add-password=$COUCHBASE_PASSWORD

