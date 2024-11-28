#!/bin/bash

set -e

#source ../.env

export IMAGE_NAME="llm-data-collector"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/../../../../secrets:/app/secrets \
    -v $(pwd)/../../../../dataset:/app/data \
    -v $(pwd)/../../../../persistent-folder:/app/persistent \
    $IMAGE_NAME \
    /bin/bash