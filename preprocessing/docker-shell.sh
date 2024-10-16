#!/bin/bash

set -e

source ../.env

export IMAGE_NAME="llm-data-preprocessor"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/../secrets:/app/secrets \
    $IMAGE_NAME \
    /bin/bash
