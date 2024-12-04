#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google.cloud import storage
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from safetensors import safe_open

load_dotenv()

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")

router = APIRouter()


# # Google Cloud credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/recipe.json"

# # Initialize Google Cloud Storage client
# client = storage.Client()

# # Load the .safetensors file from GCP bucket
# bucket_name = "recipe-dataset"
# file_name = "finetuned_model/model.safetensors"

# bucket = client.get_bucket(bucket_name)
# blob = bucket.blob(file_name)

# local_file_path = "/app/model.safetensors"
# blob.download_to_filename(local_file_path)

# # Load the fine-tuned model
# model_name = "facebook/opt-125m"
# finetuned_tokenizer = AutoTokenizer.from_pretrained(
#     model_name, use_auth_token=hf_token
# )
# finetuned_model = AutoModelForCausalLM.from_pretrained(
#     model_name, use_auth_token=hf_token
# )

# # Load the fine-tuned model weights from the safetensors file
# state_dict = {}
# with safe_open(local_file_path, framework="pt", device="cpu") as f:
#     for key in f.keys():
#         state_dict[key] = f.get_tensor(key)
# finetuned_model.load_state_dict(state_dict, strict=False)
# finetuned_model.eval()


def initialize_storage_client():
    # TODO: replace this
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("MODEL_LOADING_CREDENTIALS", "/secrets/recipe.json")
    ## Uncomment if Local Development; commen out if Ansible / Kubernetes
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/recipe.json"
    return storage.Client()


def load_model_and_tokenizer():
    # Load the .safetensors file from GCP bucket
    try:
        client = initialize_storage_client()
        bucket_name = "recipe-dataset"
        file_name = "finetuned_model/model.safetensors"

        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        local_file_path = "/app/model.safetensors"
        blob.download_to_filename(local_file_path)

        # Load the fine-tuned model
        model_name = "facebook/opt-125m"
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, use_auth_token=hf_token
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name, use_auth_token=hf_token
        )

        # Load the fine-tuned model weights from the safetensors file
        state_dict = {}
        with safe_open(local_file_path, framework="pt", device="cpu") as f:
            for key in f.keys():
                state_dict[key] = f.get_tensor(key)
        model.load_state_dict(state_dict, strict=False)
        model.eval()

        return model, tokenizer
    except Exception as e:
        raise RuntimeError(f"Error loading model and tokenizer: {str(e)}")


class RecipeRequest(BaseModel):
    ingredients: str
    dietary_preference: str
    meal_type: str
    cooking_time: int


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

    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return full_output[len(prompt):].strip()


@router.post("/llm")
async def create_recipe(request: RecipeRequest):
    prompt = (
        f"Please write a {request.dietary_preference} recipe for "
        f"{request.meal_type} that takes approximately "
        f"{request.cooking_time} minutes and includes "
        f"the following ingredients: {request.ingredients}."
    )

    try:
        finetuned_model, finetuned_tokenizer = load_model_and_tokenizer()
        recipe = generate_recipe(finetuned_model, finetuned_tokenizer, prompt)
        return {"recipe": recipe}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
