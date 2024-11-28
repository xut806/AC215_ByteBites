#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import pandas as pd
from io import BytesIO
from google.cloud import storage
from datasets import Dataset


def download_data_from_gcs(bucket_name, file_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    data_bytes = blob.download_as_bytes()
    return pd.read_json(BytesIO(data_bytes), lines=True)


def clean_data(data, phrase_to_replace, replacement_text):
    data["prompt"] = data["prompt"].str.replace(
        phrase_to_replace, replacement_text, regex=False
    )
    return data


def filter_data(data):
    data["prompt_length"] = data["prompt"].apply(len)
    data["response_length"] = data["completion"].apply(len)
    return data[(data["prompt_length"] <= 470) & (data["response_length"] <= 2500)]


def upload_to_gcp(data, bucket_name, destination_blob_name):
    client = storage.Client()
    buffer = BytesIO()
    data.to_json(buffer, orient="records", lines=True)
    blob = client.get_bucket(bucket_name).blob(destination_blob_name)
    blob.upload_from_string(buffer.getvalue(), content_type="application/json")
    print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}.")


def formatting_prompt(examples):
    EOS_TOKEN = "<|end_of_text|>"
    data_prompt = """Write a recipe that includes clear instructions and ingredients.
    Ensure the recipe has a detailed list of ingredientsand step-by-step cooking instructions.

                    ### Input:
                    {}

                    ### Response:
                    {}"""
    inputs = examples["prompt"]
    outputs = examples["completion"]
    texts = []
    for input_, output in zip(inputs, outputs):
        text = data_prompt.format(input_, output) + EOS_TOKEN
        texts.append(text)
    return {"text": texts}


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/data-service-account.json"

    bucket_name = "ai-recipe-data"
    file_name = "processed/fine_tuning_opt125_data.jsonl"
    data = download_data_from_gcs(bucket_name, file_name)

    print("Cleaning and filtering data...")
    phrase_to_replace = ("The recipe should be formatted with a clear list of ingredients "
                         "and detailed, step-by-step cooking instructions.")
    data = clean_data(data, phrase_to_replace, replacement_text=".")
    filtered_data = filter_data(data)

    destination_blob_name = "processed/fine_tuning_llama_data.jsonl"
    print("Uploading filtered data...")
    upload_to_gcp(filtered_data, bucket_name, destination_blob_name)

    print("Spliting train and val data...")
    dataset = Dataset.from_pandas(filtered_data)
    train_data, val_data = dataset.train_test_split(test_size=0.2, seed=42).values()
    train_data = train_data.map(formatting_prompt, batched=True)

    print("Uploading train and val data...")
    upload_to_gcp(
        train_data, bucket_name, "processed/fine_tuning_llama_train_data.jsonl"
    )
    upload_to_gcp(val_data, bucket_name, "processed/fine_tuning_llama_val_data.jsonl")


if __name__ == "__main__":
    main()
