#!/usr/bin/env python3

import os
from google.cloud import storage
import pandas as pd

# Set up GCP credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/data-service-account.json"

def fetch_data(bucket_name, source_blob_name, destination_file):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # Download data
    blob.download_to_filename(destination_file)
    print(f"Data fetched from gs://{bucket_name}/{source_blob_name} to {destination_file}")

def main():
    bucket_name = "ai-recipe-data"
    source_blob_name = "raw/recipe_prompts.jsonl"
    destination_file = "/app/data/recipe_prompts.jsonl"

    fetch_data(bucket_name, source_blob_name, destination_file)

if __name__ == "__main__":
    main()
