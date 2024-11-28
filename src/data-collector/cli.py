#!/usr/bin/env python3

import os
from google.cloud import storage

# Set up GCP credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/data-service-account.json"

# def fetch_data(bucket_name, source_blob_name, destination_file):
#     client = storage.Client()
#     bucket = client.bucket(bucket_name)
#     blob = bucket.blob(source_blob_name)

#     # Download data
#     blob.download_to_filename(destination_file)
#     print(f"Data fetched from gs://{bucket_name}/{source_blob_name} to {destination_file}")


def upload_to_gcp(data_path, bucket_name, destination_blob_name):
    client = storage.Client()
    blob = client.get_bucket(bucket_name).blob(destination_blob_name)
    with open(data_path, "rb") as file_data:
        blob.upload_from_file(file_data, content_type="application/json")

    print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}.")


def main():
    bucket_name = "ai-recipe-data"
    destination_blob_name = "raw/recipe_prompts.jsonl"
    data = "persistent/recipe_prompts.jsonl"

    upload_to_gcp(data, bucket_name, destination_blob_name)


if __name__ == "__main__":
    main()
