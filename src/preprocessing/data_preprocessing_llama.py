import pandas as pd
from datasets import Dataset, DatasetDict
from google.cloud import storage
from io import BytesIO, StringIO
import os

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/data-service-account.json'

client = storage.Client()

bucket_name = 'ai-recipe-data'
file_name = 'processed/fine_tuning_opt125_data.jsonl'

bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)
data_bytes = blob.download_as_bytes()

data = pd.read_json(BytesIO(data_bytes), lines=True)

phrase_to_replace = "The recipe should be formatted with a clear list of ingredients and detailed, step-by-step cooking instructions."
replacement_text = "."
data['prompt'] = data['prompt'].str.replace(phrase_to_replace, replacement_text, regex=False)

# Apply filtering by adding the length columns to the DataFrame
data['prompt_length'] = data['prompt'].apply(len)
data['response_length'] = data['completion'].apply(len)

# Filter rows based on length criteria
filtered_data = data[(data['prompt_length'] <= 470) & (data['response_length'] <= 2500)]

jsonl_data = filtered_data.to_json(orient='records', lines=True)
destination_blob_name = 'processed/fine_tuning_llama_data.jsonl'
blob.upload_from_string(jsonl_data, content_type="application/json")
print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}.")


dataset = Dataset.from_pandas(filtered_data)

data_prompt = """Write a recipe that includes clear instructions and ingredients. Ensure the recipe has a detailed list of ingredients and step-by-step cooking instructions.

### Input:
{}

### Response:
{}"""

EOS_TOKEN = "<|end_of_text|>"

def formatting_prompt(examples):
    inputs = examples["prompt"]
    outputs = examples["completion"]
    texts = []
    for input_, output in zip(inputs, outputs):
        text = data_prompt.format(input_, output) + EOS_TOKEN
        texts.append(text)
    return {"text": texts}
    
train_data, val_data = dataset.train_test_split(test_size=0.2, seed=42).values()
train_data = train_data.map(formatting_prompt, batched=True)
split_data = DatasetDict({
    'train': train_data,
    'validation': val_data
})

def upload_to_gcp(dataset, bucket_name, destination_blob_name):
    buffer = BytesIO()
    dataset.to_json(buffer, orient="records", lines=True)
    blob = client.get_bucket(bucket_name).blob(destination_blob_name)
    blob.upload_from_string(buffer.getvalue(), content_type="application/json")
    print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}.")

    
destination_train_blob = 'processed/fine_tuning_llama_train_data.jsonl'
destination_val_blob = 'processed/fine_tuning_llama_val_data.jsonl'

upload_to_gcp(filtered_data, bucket_name, destination_train_blob)

upload_to_gcp(split_data['train'], bucket_name, destination_train_blob)
upload_to_gcp(split_data['validation'], bucket_name, destination_val_blob)
