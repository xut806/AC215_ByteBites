from kfp import dsl


# Define a Container Component
@dsl.component(
    base_image="pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel", packages_to_install=["google-cloud-aiplatform"]
)
def model_finetune(
    project: str = "ai-recipe-441518",
    location: str = "us-central1",
    staging_bucket: str = "ai-recipe-staging",
    bucket_name: str = "ai-recipe-trainer",
    model_name: str = "llama3b",
):
    print("Model Finetune Job")
    
    from google.cloud import aiplatform

    project = "ai-recipe-441518"

    container_image_uri = f"gcr.io/{project}/llm-finetuner:v4"
    location = "us-central1"

    aiplatform.init(project=project,
                    location=location,
                    staging_bucket="gs://ai-recipe-trainer")
    
    job = aiplatform.CustomContainerTrainingJob(
        display_name="llama_3b_finetuning",
        container_uri=container_image_uri,
        project=project,
        location=location
    )
    
    replica_count = 1
    machine_type = "a2-highgpu-1g"
    accelerator_type = "NVIDIA_TESLA_A100"
    accelerator_count = 1

    job.run(
        replica_count=replica_count,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        sync=True
    )

    
# Define a Container Component
@dsl.component(
    base_image="python:3.11", packages_to_install=["google-cloud-aiplatform"]
)
def model_deploy(
    bucket_name: str = "",
):
    print("Model Training Job")

    import google.cloud.aiplatform as aip

    # List of prebuilt containers for prediction
    # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
    serving_container_image_uri = (
        "us-central1-docker.pkg.dev/ai-recipe-441518/llama-server-repo"
    )

    display_name = "AI Recipe Model"
    ARTIFACT_URI = f"gs://{bucket_name}/finetuned_models"

    # Upload and Deploy model to Vertex AI
    # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_upload
    deployed_model = aip.Model.upload(
        display_name=display_name,
        artifact_uri=ARTIFACT_URI,
        serving_container_image_uri=serving_container_image_uri,
    )
    print("deployed_model:", deployed_model)
    # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_deploy
    endpoint = deployed_model.deploy(
        deployed_model_display_name=display_name,
        traffic_split={"0": 100},
        machine_type="n1-standard-4",
        accelerator_type="nvidia-tesla-p100"
        accelerator_count=1,
        sync=True,
    )
    print("endpoint:", endpoint)