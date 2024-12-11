#!/bin/bash

# Set the image name
export IMAGE_NAME="api-service"

# Build the Docker image
docker build -t $IMAGE_NAME .

# Run the container with volume mounts
docker run --rm \
    --name $IMAGE_NAME \
    -p 9000:9000 \
    -v $(pwd)/../../secrets:/app/secrets \
    -v $(pwd)/../.env:/app/.env \
    $IMAGE_NAME
