# utils.py
import json
from torch.utils.data import Dataset
import torch
from google.cloud import storage
import os

class RecipeDataset(Dataset):
    def __init__(self, bucket_name, file_name, tokenizer, max_length=512):
        self.data = []
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Set up GCS client
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'
        storage_client = storage.Client()

        # Get the bucket and blob
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download the content as a string
        content = blob.download_as_text()

        # Parse the JSONL content
        for line in content.split('\n'):
            if line.strip():
                recipe = json.loads(line)
                self.data.append(recipe)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        recipe = self.data[idx]
        text = f"{recipe['prompt']}{recipe['completion']}"
        
        encodings = self.tokenizer(text, truncation=True, padding='max_length', max_length=self.max_length)
        
        # Create labels (same as input_ids for causal language modeling)
        encodings['labels'] = encodings['input_ids'].copy()

        return {key: torch.tensor(val) for key, val in encodings.items()}
