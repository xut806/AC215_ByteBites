#!/bin/bash

# set -e

export IMAGE_NAME="ai-recipe-workflow"
export BASE_DIR=$(pwd)
export GCS_PACKAGE_URI="gs://ai-recipe-trainer-code"

# Build the image based on the Dockerfile
docker build --platform linux/amd64 -t $IMAGE_NAME -f Dockerfile .
# docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .


# Run Container
docker run --rm --name $IMAGE_NAME -ti \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$BASE_DIR":/app \
    -v $(realpath secrets/):/app/secrets/ \
    -v "$BASE_DIR/data-collector":/app/data-collector \
    -v "$BASE_DIR/data-processor":/app/data-processor \
    -v $(pwd)/../../../../secrets/ml-workflow.json:/app/secrets/ml-workflow.json \
    -v $(pwd)/../../../../secrets/data-service-account.json:/app/secrets/data-service-account.json \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/ml-workflow.json \
    -e GCP_PROJECT="ai-recipe-441518" \
    -e GCS_BUCKET_NAME="ai-recipe-data" \
    -e GCS_SERVICE_ACCOUNT="ml-workflow-705@ai-recipe-441518.iam.gserviceaccount.com" \
    -e GCP_REGION="us-central1" \
    -e GCS_PACKAGE_URI="gs://ai-recipe-trainer-code" \
    $IMAGE_NAME
