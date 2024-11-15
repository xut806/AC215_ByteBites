import pandas as pd
from google.cloud import storage
from io import BytesIO
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
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(destination_blob_name)

# Write JSONL data directly to GCP bucket
blob.upload_from_string(jsonl_data, content_type="application/json")

print(f"Data successfully uploaded to gs://{bucket_name}/{destination_blob_name}.")
