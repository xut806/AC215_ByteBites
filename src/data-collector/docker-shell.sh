#!/bin/bash

set -e

export IMAGE_NAME="llm-data-collector"
export GCP_PROJECT="ai-recipe-441518"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run --rm --name $IMAGE_NAME -ti \
    -v $(pwd):/app \
    -v $(pwd)/../../../../secrets:/app/secrets \
    -v $(pwd)/../../../../dataset:/app/persistent \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/data-service-account.json \
    -e GCP_PROJECT=$GCP_PROJECT \
    $IMAGE_NAME