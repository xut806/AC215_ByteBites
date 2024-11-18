# import os
# os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'

import json
import os
from io import BytesIO

import torch
from google.cloud import storage
from huggingface_hub import login
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer,
                          TrainingArguments)
from utils import RecipeDataset

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# Load tokenizer and model from Hugging Face
model_name = "facebook/opt-125m"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token)

# Set the padding token
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id

# Initialize GCS client
storage_client = storage.Client()

# Specify your bucket name and file name
bucket_name = "recipe-dataset"
file_name = "processed/fine_tuning_data_top_5000.jsonl"

# Create the dataset
dataset = RecipeDataset(bucket_name, file_name, tokenizer)

# Define training arguments
training_args = TrainingArguments(
    output_dir="/app/finetuned_model",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=5e-5,
    logging_dir="/app/logs",
    logging_steps=10,
    save_steps=50,
    eval_strategy="steps",
    eval_steps=50,
    save_total_limit=1,
    fp16=False,
    max_grad_norm=0.3,
    remove_unused_columns=True,  
)

# Split dataset into train and validation
train_size = int(0.9 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

# Create a data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,  
)

# Fine-tune the model
trainer.train()

trainer.save_model("/app/finetuned_model")
tokenizer.save_pretrained("/app/finetuned_model")
# trainer.save_model("./finetuned_model")
# tokenizer.save_pretrained("./finetuned_model")
