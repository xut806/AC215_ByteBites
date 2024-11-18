#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from google.cloud import storage

# Set the Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/recipe.json"

bucket_name = "recipe-dataset"


def upload_weights_to_gcs(bucket_name, source_file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file)
    print(f"Successfully Uploaded {source_file} to {destination_blob_name}")


source_file = "/app/finetuned_model/model.safetensors"
destination_blob_name = "finetuned_model/model.safetensors"

upload_weights_to_gcs(bucket_name, source_file, destination_blob_name)
