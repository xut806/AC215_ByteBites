import argparse
from trl import SFTConfig, SFTTrainer
import torch
from datasets import Dataset, load_dataset
import pandas as pd
from unsloth import FastLanguageModel
from google.cloud import storage
from io import BytesIO
import os
import subprocess
import shutil
import wandb
from huggingface_hub import login
from eval import evaluate_model
import zipfile
import re

# logging_dir = "/app/logs"

# # Check if the directory exists; if not, create it
# if not os.path.exists(logging_dir):
#     os.makedirs(logging_dir)


def check_cuda_version():
    try:
        result = subprocess.run(
            ["nvcc", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except FileNotFoundError:
        print("CUDA Toolkit is not installed or 'nvcc' is not in your PATH.")


def run_nvidia_smi():
    try:
        # Run the nvidia-smi command
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        # Print the output
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except FileNotFoundError:
        print("nvidia-smi command not found. "
              "Make sure NVIDIA drivers are installed and "
              "nvidia-smi is in your PATH.")


def upload_to_gcs(bucket_name, destination_blob_name, source_file_path):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {destination_blob_name}.")
    except Exception as e:
        print(f"Failed to upload {source_file_path} "
              f"to {bucket_name}/{destination_blob_name}: {e}")

def get_latest_checkpoint(destination_folder="./finetuned_model"):
    try:
        checkpoints = [d for d in os.listdir(destination_folder) if os.path.isdir(os.path.join(destination_folder, d))]
        sorted_checkpoints = sorted(checkpoints, key=lambda x: int(re.search(r'\d+', x).group()))
        if not sorted_checkpoints:
            raise Exception("No checkpoints found in the extracted model directory.")
            
        base_folder = destination_folder[2:] if destination_folder.startswith("./") else destination_folder
        return f"{base_folder}/{sorted_checkpoints[-1]}"
    except Exception as e:
        print(f"Error finding the latest checkpoint: {e}")

def download_and_extract_model(bucket_name="ai-recipe-trainer", blob_name = "finetuned_models/finetuned_model.zip", local_file_path = "finetuned_model.zip", destination_folder="./finetuned_model"):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(local_file_path)

        print(f"Downloaded {blob_name} from {bucket_name} to {local_file_path}")
        os.makedirs(destination_folder, exist_ok=True)
        
        with zipfile.ZipFile(local_file_path, "r") as zip_ref:
            zip_ref.extractall(destination_folder)
            print(f"Extracted model files to {destination_folder}")
        
        model_id = get_latest_checkpoint(destination_folder=destination_folder)
        print(f"Old model's checkpoint identified: {model_id}")
        return model_id
    
    except Exception as e:
        print(f"Failed to download or extract the model: {e}")

def load_and_prepare_model(model_id="finetuned_model/checkpoint-500", max_seq_length=2048, load_in_4bit = True):
    try:
        print(f"Loading model from: {model_id}")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_id,
            max_seq_length=max_seq_length,
            load_in_4bit=load_in_4bit
        )
        print("Old Finetuned model and tokenizer loaded successfully.")
        return model, tokenizer

    except Exception as e:
        print(f"Failed to load model: {e}")


def main(args):
    if not args.train:
        print("Train flag not set. Exiting script.")
        return

    bucket_name = 'ai-recipe-data'
    train_blob_name = 'processed/fine_tuning_llama_train_data.jsonl'
    val_blob_name = 'processed/fine_tuning_llama_val_data.jsonl'
    val_data_path = f"gs://{bucket_name}/{val_blob_name}"
    MODEL_NAME = 'unsloth/Llama-3.2-3B-bnb-4bit'

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
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj",
                        "up_proj", "down_proj", "o_proj", "gate_proj"],
        use_rslora=True,
        use_gradient_checkpointing="unsloth",
        random_state=32,
        loftq_config=None,
    )

    model.gradient_checkpointing_enable()

    learning_rate = 3e-4
    epochs = 1
    batch_size = 1  # 4
    NAME = "Llama-3.2-3B-bnb-4bit"

    wandb.login(key=os.environ['WANDB_API'])

    wandb.init(
        project="ai-recipe",
        config={
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,  # per device
            "model_name": NAME,
        },
        name=NAME,
    )
    # test
    epochs=1
    batch_size=1 #4
    max_steps=2
    gradient_accumulation_steps=1

    # epochs = 3
    # batch_size = 4
    # max_steps = -1
    # gradient_accumulation_steps = 4
    output_dir = "/app/finetuned_model"
    logging_dir = "/app/logs"

    training_args = SFTConfig(
        learning_rate=learning_rate,
        lr_scheduler_type="linear",
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,  # 4
        num_train_epochs=epochs,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=50,
        max_steps=max_steps,
        optim="adamw_8bit",
        weight_decay=0.01,
        # 10% of training steps for warmup
        warmup_steps=int(0.1 * (len(train_data) / 2)),
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

    # Evaluation: Old vs New model
    print("Evaluating start...")
    eva_dataset = load_dataset('json', data_files={'validation': val_data_path}, split='validation')
    new_model_bleu = evaluate_model(model, tokenizer, eval_dataset=eva_dataset, device=torch.device("cuda"))

    old_model_id = download_and_extract_model(bucket_name="ai-recipe-trainer", blob_name = "finetuned_models/finetuned_model.zip", local_file_path = "finetuned_model.zip", destination_folder="./finetuned_model")
    old_model, old_tokenizer = load_and_prepare_model(model_id=old_model_id, max_seq_length=2048, load_in_4bit = True)
    old_model_bleu = evaluate_model(old_model, old_tokenizer, eval_dataset=eva_dataset, device=torch.device("cuda"))
    print(f"New model's BlUE score: {new_model_bleu}, old model's BLUE score: {old_model_bleu}")
    print("Evaluating end...")

    if (old_model_bleu<=new_model_bleu):
        print("Saving new model to Wandb...")
        artifact_name = "finetuned_model"
        artifact = wandb.Artifact(name=artifact_name, type="model")
        artifact.add_dir(output_dir)
        wandb.log_artifact(artifact)

        print("Saving new model weights to GCS...")
        bucket_name2 = 'ai-recipe-trainer'
        model_zip_path = "/app/finetuned_model.zip"
        destination_blob_name = "finetuned_models/finetuned_model.zip"

        shutil.make_archive(
            base_name=model_zip_path.replace('.zip', ''),
            format='zip',
            root_dir=output_dir)
        print(f"Model zipped at {model_zip_path}")

        upload_to_gcs(bucket_name2, destination_blob_name, model_zip_path)

        # Zip the output directory
        # subprocess.run(["zip", "-r", model_zip_path, output_dir])

        # Upload to GCS
        # upload_to_gcs(bucket_name2, gcs_blob_name, model_zip_path)

        print("Model weights successfully uploaded to GCS.")

        wandb.finish()

#    model.save_pretrained_merged("model", tokenizer,
#    save_method = "merged_16bit",)
#    model.push_to_hub_merged("hf/model", tokenizer,
#    save_method = "merged_16bit", token = "")


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
