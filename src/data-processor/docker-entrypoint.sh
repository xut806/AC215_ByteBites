#!/bin/bash

echo "Container is running!!!"

args="$@"
echo $args

if [[ -z ${args} ]]; 
then
    # Authenticate gcloud using service account
    gcloud auth activate-service-account --key-file=/app/secrets/data-service-account.json
    # Set GCP Project Details
    gcloud config set project ai-recipe-441518
    #/bin/bash
    pipenv shell
else
  pipenv run python $args
fi