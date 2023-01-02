#!/bin/bash

# Set GCP environment variables
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service.json"

# Set GCP project ID
export GOOGLE_CLOUD_PROJECT="upwork-python-automation"

# Set GCP zone
export GOOGLE_CLOUD_ZONE="europe-west9-a"

echo "Starting the GCP application..."
echo "GCP project ID: $GOOGLE_CLOUD_PROJECT"
echo "GCP zone: $GOOGLE_CLOUD_ZONE"
echo "GCP credentials: $GOOGLE_APPLICATION_CREDENTIALS"

# Launch the app
python3 main.py

