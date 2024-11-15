from google.cloud import aiplatform
import os


# GCP project where the serverless training job will run
project = "ai-recipe-441518"

#Defining the container image URI to be used for training
container_image_uri = f"gcr.io/{project}/llm-finetuner:v0"
location = "us-central1"

# Initialize AI Platform with a staging bucket
aiplatform.init(project=project, location=location, staging_bucket="gs://ai-recipe-trainer")

# Create a custom container training job
job = aiplatform.CustomContainerTrainingJob(
    display_name="llama_3b_finetuning",
    container_uri = container_image_uri,
    project = project,
    location = location
)

# Specify the configuration for the training job
replica_count = 1
machine_type = "n1-standard-4"
accelerator_type = "ACCELERATOR_TYPE_UNSPECIFIED"
accelerator_count = 0

# Start the training job with the specified configuration
job.run(
    replica_count = replica_count,
    machine_type = machine_type,
    accelerator_type = accelerator_type,
    accelerator_count = accelerator_count,
    sync=False
)
