#!/bin/bash

set -e

source ../.env

export IMAGE_NAME="llm-fine-tuner"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/../../secrets:/app/secrets \
    -v $(pwd)/../.env:/app/.env \
    $IMAGE_NAME \
    /bin/bash

