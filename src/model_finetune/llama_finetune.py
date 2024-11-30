import argparse
from trl import SFTConfig, SFTTrainer
import torch
from datasets import Dataset
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from unsloth import is_bfloat16_supported
import wandb
from huggingface_hub import login
from unsloth import FastLanguageModel
from google.cloud import storage
from io import BytesIO
import os
import subprocess
import shutil

# logging_dir = "/app/logs"

# # Check if the directory exists; if not, create it
# if not os.path.exists(logging_dir):
#     os.makedirs(logging_dir)

    
def check_cuda_version():
    try:
        result = subprocess.run(["nvcc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except FileNotFoundError:
        print("CUDA Toolkit is not installed or 'nvcc' is not in your PATH.")

def run_nvidia_smi():
    try:
        # Run the nvidia-smi command
        result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Print the output
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except FileNotFoundError:
        print("nvidia-smi command not found. Make sure NVIDIA drivers are installed and nvidia-smi is in your PATH.")

    
def upload_to_gcs(bucket_name, destination_blob_name, source_file_path):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Upload the file
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {destination_blob_name}.")
    except Exception as e:
        print(f"Failed to upload {source_file_path} to {bucket_name}/{destination_blob_name}: {e}")



def main(args):

    if not args.train:
        print("Train flag not set. Exiting script.")
        return

    bucket_name = 'ai-recipe-data'
    project_id = 'ai-recipe-441518'
    train_blob_name = 'processed/fine_tuning_llama_train_data.jsonl'
    MODEL_NAME = 'unsloth/Llama-3.2-3B-bnb-4bit'
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/data-service-account.json'
    wandb_api_key = "50a87c65b5e1dd57a23910ad46496b75cc6a0e0b"
    huggingface_token = "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"
    print("Hugging Face Token fetched successfully.")
    os.environ["WANDB_API"] = wandb_api_key
    os.environ["HF_TOKEN"] = huggingface_token


    # client = storage.Client.from_service_account_json(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(train_blob_name)
    train_data_bytes = blob.download_as_bytes()
    train_data = pd.read_json(BytesIO(train_data_bytes), lines=True)
    train_data = Dataset.from_pandas(train_data)

    print("**train_data: **", train_data)

    login(token=os.environ['HF_TOKEN'])
    
    torch.cuda.empty_cache()
    MAX_SEQ_LENGTH = 2048
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
        dtype=None,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=16,
        lora_dropout=0,
        bias = "none",
        target_modules=["q_proj", "k_proj", "v_proj", "up_proj", "down_proj", "o_proj", "gate_proj"],
        use_rslora=True,
        use_gradient_checkpointing="unsloth",
        random_state=32,
        loftq_config=None,
    )

    model.gradient_checkpointing_enable()
    
    learning_rate=3e-4
    epochs=1
    batch_size= 1 #4
    NAME="Llama-3.2-3B-bnb-4bit"

    wandb.login(key=os.environ['WANDB_API'])

    wandb.init(
        project="ai-recipe",
        config={
        "learning_rate": learning_rate,
        "epochs": epochs,
        "batch_size": batch_size, #per device
        "model_name": NAME,
        },
        name=NAME,
    )
    #test
    # epochs=1
    # batch_size=1 #4
    # max_steps=2
    # gradient_accumulation_steps=1
    
    epochs=3
    batch_size= 4 #4
    max_steps=-1
    gradient_accumulation_steps=4
    output_dir = "/app/finetuned_model"
    logging_dir = "/app/logs"

    training_args = SFTConfig(
        learning_rate=learning_rate,
        lr_scheduler_type="linear",
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,#4
        num_train_epochs=epochs,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=50,
        max_steps=max_step,
        optim="adamw_8bit",
        weight_decay=0.01,
        warmup_steps=int(0.1 * (len(train_data) / 2)), # 10% of training steps for warmup
        output_dir=output_dir,
        logging_dir=logging_dir,
        seed=0,
        remove_unused_columns=True,
        run_name="test_v0",
        report_to="wandb" 
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_data,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_num_proc=2,
        packing=True,
        args=training_args,
    )
    print("Training start...")
    trainer.train()
    print("Training finished...")

    # Displaying the results
#     print("Files in output_dir:")
#     print(output_files)

#     print("\nFiles in logging_dir:")
#     print(logging_files)
    print("Saveing model to Wandb...")
    artifact_name = "finetuned_model"
    artifact = wandb.Artifact(name=artifact_name, type="model")
    artifact.add_dir(output_dir)
    wandb.log_artifact(artifact)
    
    print("Saving model weights to GCS...")

    # Define paths
    bucket_name2 = 'ai-recipe-trainer'
    model_zip_path = "/app/finetuned_model.zip"
    destination_blob_name = "finetuned_models/finetuned_model.zip"
    
    shutil.make_archive(base_name=model_zip_path.replace('.zip', ''), format='zip', root_dir=output_dir)
    print(f"Model zipped at {model_zip_path}")
    
    upload_to_gcs(bucket_name2, destination_blob_name, model_zip_path)

    # Zip the output directory
    # subprocess.run(["zip", "-r", model_zip_path, output_dir])

    # Upload to GCS
    # upload_to_gcs(bucket_name2, gcs_blob_name, model_zip_path)

    print("Model weights successfully uploaded to GCS.")

    wandb.finish()
    
#    model.save_pretrained_merged("model", tokenizer, save_method = "merged_16bit",)
#    model.push_to_hub_merged("hf/model", tokenizer, save_method = "merged_16bit", token = "")

if __name__ == "__main__":
    print("System information...")
    run_nvidia_smi()
    check_cuda_version()
    parser = argparse.ArgumentParser(description="Llama fine-tuning script")
    parser.add_argument(
        "--train",
        action="store_true",
        help="Flag to start the training process",
    )
    args = parser.parse_args()
    main(args)
    
