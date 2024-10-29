#!/bin/bash

set -e

source ../.env

export IMAGE_NAME="ocr-ner-ingredient-extractor"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/../../secrets:/app/secrets \
    $IMAGE_NAME \
    /bin/bash
