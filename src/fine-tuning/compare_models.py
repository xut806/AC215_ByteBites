#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dotenv import load_dotenv
from google.cloud import storage
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from safetensors import safe_open

# Load environment variables from .env file
load_dotenv()

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/recipe.json"

# Initialize Google Cloud Storage client
client = storage.Client()

# Load the .safetensors file from GCP bucket
bucket_name = "recipe-dataset"
file_name = "finetuned_model/model.safetensors"

bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)

local_file_path = "/app/model.safetensors"
blob.download_to_filename(local_file_path)


def generate_recipe(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            inputs.input_ids,
            max_length=350,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.75,
            repetition_penalty=1.2,
        )

    # Decode the output, excluding the input prompt
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return full_output[len(prompt):].strip()


# Load the original model
original_model_name = "facebook/opt-125m"
original_tokenizer = AutoTokenizer.from_pretrained(
    original_model_name, use_auth_token=hf_token
)
original_model = AutoModelForCausalLM.from_pretrained(
    original_model_name, use_auth_token=hf_token
)

# Load the fine-tuned model
# finetuned_model_path = "/app/finetuned_model"
# "/app/finetuned_model"
finetuned_tokenizer = AutoTokenizer.from_pretrained(
    original_model_name, use_auth_token=hf_token
)
finetuned_model = AutoModelForCausalLM.from_pretrained(
    original_model_name, use_auth_token=hf_token
)

# Load the fine-tuned model weights from the safetensors file
state_dict = {}
with safe_open(local_file_path, framework="pt", device="cpu") as f:
    for key in f.keys():
        state_dict[key] = f.get_tensor(key)
finetuned_model.load_state_dict(state_dict, strict=False)
finetuned_model.eval()

# Prepare your prompt
prompt = """Please write a low-sodium meal recipe that takes
            approximately 55 minutes and includes the following
            ingredients: tomato, beef.
            The recipe should be formatted with a clear list of
            ingredients and detailed,
            step-by-step cooking instructions."""

# Generate recipes using both models
original_recipe = generate_recipe(original_model, original_tokenizer, prompt)
finetuned_recipe = generate_recipe(
    finetuned_model, finetuned_tokenizer, prompt
)

# Print the results
print("Original Model Output:")
print(original_recipe)
print("\n" + "=" * 50 + "\n")
print("Fine-tuned Model Output:")
print(finetuned_recipe)
