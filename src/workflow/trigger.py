import os
from google.cloud import aiplatform
import functions_framework

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data
    print(f"Received data: {data}")
    bucket = data["bucket"]
    name = data["name"]
    BUCKET_NAME = "ai-recipe-data"
    if bucket == BUCKET_NAME and name == "raw/recipe_prompts.jsonl":
        print(f"Detected change to {name} in bucket {bucket}.")

        trigger_pipeline_logic(name)
    else:
        print("Event is not related to the pipeline YAML. Ignoring.")

def trigger_pipeline_logic(file_name):
    """Logic to trigger the pipeline."""
    PROJECT_ID = "ai-recipe-441518"
    REGION = "us-central1"
    PIPELINE_ROOT = "gs://ai-recipe-data/pipeline_root"
    PIPELINE_YAML = "pipeline.yaml"
    try:
        print(f"Triggering pipeline for {file_name}...")
        aiplatform.init(
            project=PROJECT_ID,
            location=REGION,
        )
        job = aiplatform.PipelineJob(
            display_name='llama-pipeline-cloud-function-invocation',
            template_path= f"{PIPELINE_ROOT}/{PIPELINE_YAML}",
            pipeline_root=PIPELINE_ROOT,
            enable_caching=False,
        )

        job.submit()

        print("Pipeline successfully triggered.")
    except Exception as e:
        print(f"Error triggering pipeline: {e}")