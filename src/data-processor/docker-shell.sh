#!/bin/bash

set -e

export IMAGE_NAME="llm-data-preprocessor"

docker build --platform linux/amd64 -t $IMAGE_NAME -f Dockerfile .

docker run --rm --name $IMAGE_NAME -ti \
    -v $(pwd):/app \
    -v $(pwd)/../../../../secrets/:/app/secrets/ \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/data-service-account.json \
    -e GCP_PROJECT=ai-recipe-441518 \
    $IMAGE_NAME