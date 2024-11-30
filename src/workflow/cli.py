"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py
"""

import os
import argparse
import random
import string
from kfp import dsl
from kfp import compiler
import google.cloud.aiplatform as aip
from model import model_finetune as model_finetune_job
# from model import model_finetune as model_finetune_job, model_deploy as model_deploy_job

GCP_PROJECT = "ai-recipe-441518"
GCS_BUCKET_NAME = "ai-recipe-data"
BUCKET_URI = f"gs://{GCS_BUCKET_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/root"
GCS_SERVICE_ACCOUNT = "ml-workflow-705@ai-recipe-441518.iam.gserviceaccount.com"
GCS_PACKAGE_URI = "gs://ai-recipe-trainer"
GCP_REGION = "us-central1"

DATA_COLLECTOR_IMAGE = "gcr.io/ai-recipe-441518/llm-data-collector:v1"
DATA_PROCESSOR_IMAGE = "gcr.io/ai-recipe-441518/llm-data-processor:v1"
MODEL_FINETUNE_IMAGE = "gcr.io/ai-recipe-441518/llm-finetuner:v3"


def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def data_collector():
    print("data_collector()")

    # Define a Container Component
    @dsl.container_component
    def data_collector():
        container_spec = dsl.ContainerSpec(
            image=DATA_COLLECTOR_IMAGE,
            command=["python", "cli.py"],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def data_collector_pipeline():
        data_collector()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        data_collector_pipeline, package_path="data_collector.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "ai-recipe-data-collector-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="data_collector.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def data_processor():
    print("data_processor()")

    # Define a Container Component for data processor
    @dsl.container_component
    def data_processor():
        container_spec = dsl.ContainerSpec(
            image=DATA_PROCESSOR_IMAGE,
            command=["python", "cli.py"],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def data_processor_pipeline():
        data_processor()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        data_processor_pipeline, package_path="data_processor.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "ai-recipe-data-processor-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="data_processor.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def model_finetune():
    print("model_finetune()")

    # Define a Pipeline
    @dsl.pipeline
    def model_finetune_pipeline():
        model_finetune_job(
            project=GCP_PROJECT,
            location=GCP_REGION,
            staging_bucket=GCS_PACKAGE_URI,
            bucket_name=GCS_BUCKET_NAME,
        )

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        model_finetune_pipeline, package_path="model_finetune.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "ai-recipe-model-finetune-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="model_finetune.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


# def model_deploy():
#     print("model_deploy()")
#     # Define a Pipeline
#     @dsl.pipeline
#     def model_deploy_pipeline():
#         model_deploy(
#             bucket_name=GCS_BUCKET_NAME,
#         )

#     # Build yaml file for pipeline
#     compiler.Compiler().compile(
#         model_deploy_pipeline, package_path="model_deploy.yaml"
#     )

#     # Submit job to Vertex AI
#     aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

#     job_id = generate_uuid()
#     DISPLAY_NAME = "cheese-app-model-deploy-" + job_id
#     job = aip.PipelineJob(
#         display_name=DISPLAY_NAME,
#         template_path="model_deploy.yaml",
#         pipeline_root=PIPELINE_ROOT,
#         enable_caching=False,
#     )

#     job.run(service_account=GCS_SERVICE_ACCOUNT)


def pipeline():
    print("pipeline()")
    # Define a Container Component for data collector
    @dsl.container_component
    def data_collector():
        container_spec = dsl.ContainerSpec(
            image=DATA_COLLECTOR_IMAGE,
            command=["python", "cli.py"],
        )
        return container_spec

    # Define a Container Component for data processor
    @dsl.container_component
    def data_processor():
        container_spec = dsl.ContainerSpec(
            image=DATA_PROCESSOR_IMAGE,
            command=["python", "cli.py"],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def ml_pipeline():
        # Data Collector
        data_collector_task = (
            data_collector()
            .set_display_name("Data Collector")
            .set_cpu_limit("500m")
            .set_memory_limit("2G")
        )
        # Data Processor
        data_processor_task = (
            data_processor()
            .set_display_name("Data Processor")
            .after(data_collector_task)
        )
        # Model Finetune
        model_finetune_task = (
            model_finetune_job(
                project=GCP_PROJECT,
                location=GCP_REGION,
                staging_bucket=GCS_PACKAGE_URI,
                bucket_name=GCS_BUCKET_NAME,
                model_name="llama3b",
            )
            .set_display_name("Model Finetune")
            .after(data_processor_task)
        )
        
        # # Model Deployment
        # model_deploy_task = (
        #     model_deploy_job(
        #         bucket_name=GCS_BUCKET_NAME,
        #     )
        #     .set_display_name("Model Deploy")
        #     .after(model_training_task)
        # )

    # Build yaml file for pipeline
    compiler.Compiler().compile(ml_pipeline, package_path="pipeline.yaml")

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "ai-recipe-pipeline-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="pipeline.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def sample_pipeline():
    print("sample_pipeline()")
    # Define Component
    @dsl.component
    def square(x: float) -> float:
        return x**2

    # Define Component
    @dsl.component
    def add(x: float, y: float) -> float:
        return x + y

    # Define Component
    @dsl.component
    def square_root(x: float) -> float:
        return x**0.5

    # Define a Pipeline
    @dsl.pipeline
    def sample_pipeline(a: float = 3.0, b: float = 4.0) -> float:
        a_sq_task = square(x=a)
        b_sq_task = square(x=b)
        sum_task = add(x=a_sq_task.output, y=b_sq_task.output)
        return square_root(x=sum_task.output).output

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        sample_pipeline, package_path="sample-pipeline1.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "sample-pipeline-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="sample-pipeline1.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def main(args=None):
    print("CLI Arguments:", args)

    if args.data_collector:
        data_collector()

    if args.data_processor:
        print("Data Processor")
        data_processor()

    if args.model_finetune:
        print("Model Finetune")
        model_finetune()

    # if args.model_deploy:
    #     print("Model Deploy")
    #     model_deploy()

    if args.pipeline:
        pipeline()

    if args.sample:
        print("Sample Pipeline")
        sample_pipeline()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Workflow CLI")

    parser.add_argument(
        "--data_collector",
        action="store_true",
        help="Run just the Data Collector",
    )
    parser.add_argument(
        "--data_processor",
        action="store_true",
        help="Run just the Data Processor",
    )
    parser.add_argument(
        "--model_finetune",
        action="store_true",
        help="Run just Model Finetune",
    )
    # parser.add_argument(
    #     "--model_deploy",
    #     action="store_true",
    #     help="Run just Model Deployment",
    # )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Cheese App Pipeline",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Sample Pipeline 1",
    )

    args = parser.parse_args()

    main(args)