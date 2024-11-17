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

# Function to list files in a directory
def list_files(directory):
    try:
        files = os.listdir(directory)
        return files
    except FileNotFoundError:
        return f"Directory '{directory}' not found."
    except PermissionError:
        return f"Permission denied for accessing '{directory}'."


def main(args):

    if not args.train:
        print("Train flag not set. Exiting script.")
        return

    bucket_name = 'ai-recipe-data'
    project_id = 'ai-recipe-441518'
    train_blob_name = 'processed/fine_tuning_llama_train_data.jsonl'
    MODEL_NAME = 'unsloth/Llama-3.2-3B-bnb-4bit'
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/data-service-account.json'
    wandb_api_key = ""
    huggingface_token = ""
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

    MAX_SEQ_LENGTH = 5020
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
        target_modules=["q_proj", "k_proj", "v_proj", "up_proj", "down_proj", "o_proj", "gate_proj"],
        use_rslora=True,
        use_gradient_checkpointing="unsloth",
        random_state=32,
        loftq_config=None,
    )

    model.gradient_checkpointing_enable()

    wandb.login(key=os.environ['WANDB_API'])

    wandb.init(project="llama_3b_finetune_gpu")
    output_dir = "/app/finetuned_model"
    logging_dir = "/app/logs"

    training_args = SFTConfig(
        learning_rate=3e-4,
        lr_scheduler_type="linear",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=1,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=50,
        max_steps=3,
        optim="adamw_8bit",
        weight_decay=0.01,
        warmup_steps=int(0.1 * (len(train_data) / 2)), # 10% of training steps for warmup
        output_dir=output_dir,
        logging_dir=logging_dir,
        seed=0,
        remove_unused_columns=True,
        run_name="test_v0"
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
    
    output_files = list_files(output_dir)
    logging_files = list_files(logging_dir)

    # Displaying the results
    print("Files in output_dir:")
    print(output_files)

    print("\nFiles in logging_dir:")
    print(logging_files)


    wandb.finish()

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
    
