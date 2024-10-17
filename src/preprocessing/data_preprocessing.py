import pandas as pd
from google.cloud import storage
from io import BytesIO
import os
import json

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'

# Initialize Google Cloud Storage client
client = storage.Client()

# Load data from GCP bucket
bucket_name = 'recipe-dataset'
file_name = 'raw/RAW_recipes.csv'

bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)
data = blob.download_as_bytes()

df = pd.read_csv(BytesIO(data))

# Select relevant columns
recipes_df = df[['name', 'tags', 'minutes', 'ingredients', 'steps']]

# Create prompt and completion pairs
def create_prompt_completion_with_preferences(row, dietary_options, meal_options):
    dietary_prefs = ", ".join([tag for tag in eval(row['tags']) if tag in dietary_options]) or "any"
    meal_type = ", ".join([tag for tag in eval(row['tags']) if tag in meal_options]) or "meal"
    
    prompt = (f"Please write a {dietary_prefs} {meal_type} recipe that takes approximately {row['minutes']} minutes "
              f"and includes the following ingredients: {', '.join(eval(row['ingredients']))}. "
              f"The recipe should be formatted with a clear list of ingredients and detailed, step-by-step cooking instructions.")
    
    ingredients = "\n".join(eval(row['ingredients']))
    steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(eval(row['steps']))])
    completion = f"Ingredients:\n{ingredients}\n\nInstructions:\n{steps}"
    
    return {"prompt": prompt, "completion": completion}

# Define dietary preferences and meal types
dietary_options = ['vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'low-carb', 'low-sodium', 'healthy']
meal_options = ['breakfast', 'lunch', 'dinner', 'brunch', 'desserts', 'soup', 'salad', 'appetizer']

# Apply the updated function to each row
formatted_data_with_preferences = [create_prompt_completion_with_preferences(row, dietary_options, meal_options) for _, row in recipes_df.iterrows()]

# Directly save the data to GCP bucket
destination_blob_name = 'processed/fine_tuning_data_top_5000.jsonl'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(destination_blob_name)

# Write data directly to GCP
with blob.open("w") as f:
    for entry in formatted_data_with_preferences[:5000]:
        f.write(json.dumps(entry) + '\n')

print(f"Data directly uploaded to {bucket_name} as {destination_blob_name}.")
