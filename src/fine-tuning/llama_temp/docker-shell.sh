#!/bin/bash

set -e

#source ../.env

export IMAGE_NAME="llm-finetune"

docker build -t $IMAGE_NAME -f Dockerfile .
docker build -t gcr.io/ai-recipe-441518/llm-finetuner:v0 .

docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/../../../secrets:/app/secrets \
    $IMAGE_NAME \
    /bin/bash
