#!/usr/bin/env python3

from google.cloud import aiplatform
import os

def train_model(project, location, bucket_name, container_image_uri):
    aiplatform.init(project=project, location=location, staging_bucket=f"gs://{bucket_name}")

    job = aiplatform.CustomContainerTrainingJob(
        display_name="llama-finetuning",
        container_uri=container_image_uri,
        project=project,
        location=location
    )

    job.run(
        replica_count=1,
        machine_type="a2-highgpu-1g",
        accelerator_type="NVIDIA_TESLA_A100",
        accelerator_count=1,
        sync=True
    )
    print("Training job complete.")

def main():
    train_model(
        project="ai-recipe-441518",
        location="us-central1",
        bucket_name="ai-recipe-trainer",
        container_image_uri="gcr.io/ai-recipe-441518/llm-finetuner:v3",
    )

if __name__ == "__main__":
    main()
