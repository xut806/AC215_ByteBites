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
    bucket_name: str = "ai-recipe-workflow-demo",
):
    print("Model Deployment Job")
    import google.cloud.aiplatform as aip

    # List of prebuilt containers for prediction
    # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
    DEPLOY_IMAGE = "us-central1-docker.pkg.dev/ai-recipe-441518/llama-server-repo/llama-server-image:test"
    HEALTH_ROUTE = "/health"
    PREDICT_ROUTE = "/generate/"
    SERVING_CONTAINER_PORTS = [8080]
    
    deployed_model = aip.Model.upload(
        display_name=f'llama-3b',    
        description=f'llama-3b with Uvicorn and FastAPI',
        serving_container_image_uri=DEPLOY_IMAGE,
        serving_container_predict_route=PREDICT_ROUTE,
        serving_container_health_route=HEALTH_ROUTE,
        serving_container_ports=SERVING_CONTAINER_PORTS,
    )
    print(deployed_model.resource_name)
    
    # Retrieve a Model on Vertex
    deployed_model = aip.Model(deployed_model.resource_name)
    
    # Deploy model
    endpoint = deployed_model.deploy(
        machine_type='n1-standard-4', 
        accelerator_type= "NVIDIA_TESLA_T4",
        accelerator_count = 1,
        traffic_split={"0": 100}, 
        min_replica_count=1,
        max_replica_count=1,
        traffic_percentage=100,
        deploy_request_timeout=1200,
        sync=True,
    )
    print("endpoint:", endpoint)
    endpoint.wait()
