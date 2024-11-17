#!/bin/bash

# Set the image name
export IMAGE_NAME="ocr"

# Build the Docker image
docker build -t $IMAGE_NAME .

# Run the container
docker run --rm --name $IMAGE_NAME -p 9000:9000 $IMAGE_NAME
