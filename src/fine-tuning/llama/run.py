#!/usr/bin/env python
# coding: utf-8


from google.cloud import aiplatform
import os

project = "ai-recipe-441518"

container_image_uri = f"gcr.io/{project}/llm-finetuner:v3"
location = "us-central1"

aiplatform.init(project=project, location=location, staging_bucket="gs://ai-recipe-trainer")

job = aiplatform.CustomContainerTrainingJob(
    display_name="llama_3b_finetuning",
    container_uri = container_image_uri,
    project = project,
    location = location
)

replica_count = 1  
machine_type = "a2-highgpu-1g"  
accelerator_type = "NVIDIA_TESLA_A100"  
accelerator_count = 1  

job.run(
    replica_count = replica_count,
    machine_type = machine_type,
    accelerator_type = accelerator_type,
    accelerator_count = accelerator_count,
    sync=True
)

