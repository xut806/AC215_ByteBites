import os
from dotenv import load_dotenv
from google.cloud import storage
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from safetensors import safe_open
import requests

# Load environment variables from .env file
load_dotenv()

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# USDA credentials
USDA_API_KEY = os.getenv("USDA_API_KEY")
#os.environ['USDA_API_KEY'] = '/app/secrets/usda_api.json'

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'

# Initialize Google Cloud Storage client
client = storage.Client()

# Load the .safetensors file from GCP bucket
bucket_name = 'recipe-dataset'
file_name = "finetuned_model/model.safetensors"

bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)

local_file_path = "/app/model.safetensors"
blob.download_to_filename(local_file_path)


def generate_recipe(model, tokenizer, prompt):
    """
    Generate recipe with LLM.
    """
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
            repetition_penalty=1.2
        )
    
    # Decode the output, excluding the input prompt
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    recipe_text = full_output[len(prompt):].strip()
    return recipe_text


def save_recipe_to_text(recipe_text, filename='generated_recipe.txt'):
    """
    Save the generated recipe to a text file.
    """
    with open(filename, 'w') as f:
        f.write(recipe_text)
    print(f"Recipe saved to {filename}")


# Load the fine-tuned model weights from the safetensors file
original_model_name = "facebook/opt-125m"
finetuned_tokenizer = AutoTokenizer.from_pretrained(original_model_name, use_auth_token=hf_token)
finetuned_model = AutoModelForCausalLM.from_pretrained(original_model_name, use_auth_token=hf_token)
state_dict = {}
with safe_open(local_file_path, framework="pt", device="cpu") as f:
    for key in f.keys():
        state_dict[key] = f.get_tensor(key)
finetuned_model.load_state_dict(state_dict, strict=False)
finetuned_model.eval()

# format the prompt using ingredients, time to complete, and dietary preference
ingredients = ["tomato", "beef"] # ingredients to cook with (user-specified)
ingredients_str = ", ".join(ingredients) # string version of the ingredients
time_to_complete = 55  # time to complete the recipe (user-specified)
dietary_preference = "low-sodium"  # dietary preference (user-specified)

prompt = f"""Please write a {dietary_preference} meal recipe that takes approximately {time_to_complete} minutes 
            and includes the following ingredients: {ingredients_str}. 
            The recipe should be formatted with a clear list of ingredients and detailed, step-by-step cooking instructions."""

# nutrition facts for the recipe
def get_nutrition_info(ingredients):
    """
    Get nutrition info for each ingredient used in the recipe using USDA API
    """
    nutrition_data = {}
    base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    for ingredient in ingredients:
        params = {
            'query': ingredient,
            'api_key': USDA_API_KEY,
            'pageSize': 3  
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['foods']:
                # we will first resort to finding values in the FNDDS database, as the database includes info on raw ingredients only
                fndds_foods = [food for food in data['foods'] if food.get('dataType') == 'Survey (FNDDS)']

                if fndds_foods:
                    # we will try to return the match with the most complete set of nutrients 
                    sorted_foods = sorted(
                        fndds_foods,
                        key=lambda x: len(x.get('foodNutrients', [])), # sort by the number of nutrients present (descending)
                        reverse=True
                    )
                    most_complete_food = sorted_foods[0]

                    if most_complete_food.get('servingSize') is None:
                        # non of the FNDDS result has a serving size, ad the serving size is a fixed value of 100g for FNDDS ingredients
                        # see: https://www.ars.usda.gov/ARSUserFiles/80400530/pdf/fndds/FNDDS_2021_2023_factsheet.pdf 
                        serving_size = 100
                        serving_size_unit = 'g'
                    print(f"Reminder: Raw ingredient data is found for {ingredient}. The nutrition calculation for this ingredient is based on values powered by the FNDDS database from USDA.")
                
                else:
                    # Fallback:
                    # if no FNDDS data is found we will use nutrition facts from other databases 
                    print(f"Reminder: No raw ingredient data is found for {ingredient}. General USDA nutrition facts search is used for nutrition calculation for this ingredient.")
                    non_fndds_foods = [food for food in data['foods'] if food.get('dataType') != 'Survey (FNDDS)']

                    if non_fndds_foods:
                        # we will try to return the match with the most complete set of nutrients 
                        sorted_foods = sorted(
                            non_fndds_foods,
                            key=lambda x: len(x.get('foodNutrients', [])),
                            reverse=True
                        )
                        most_complete_food = next(
                            (food for food in sorted_foods if food.get('servingSize') is not None), # we will try to return a result with a serving size
                            sorted_foods[0]  # if none has a serving size, we will return the result with the most complete set of nutrients
                        )
                        serving_size = most_complete_food.get('servingSize', 'N/A')
                        serving_size_unit = most_complete_food.get('servingSizeUnit', '')
                    else: # display warning message that tells user this ingredient is not included in nutrition calc
                        print(f"Warning: No nutrition data available for {ingredient}. This ingredient will not be included in the nutrition facts calculation.")
                        continue

                # store nutrition data for the ingredient 
                nutrition_data[ingredient] = {
                    'description': most_complete_food['description'],
                    'dataType': most_complete_food['dataType'],
                    'servingSize': serving_size,
                    'servingSizeUnit': serving_size_unit,
                    'nutrients': {
                        nutrient['nutrientName']: {
                            'value': nutrient['value'],
                            'unit': nutrient.get('unitName', '')
                        }
                        for nutrient in most_complete_food['foodNutrients']
                    }
                }
        else:
            print(f"Failed to retrieve data for {ingredient}")
    
    return nutrition_data

def aggregate_nutrition_info_with_units(nutrition_info_dict):
    """
    Aggregates the nutrients info for each ingredient, 
    and scaling the serving size to display nutrition facts for 100g
    """
    overall_nutrition = {}

    # Aggregate the nutrients from each ingredient, scaling to 100g
    for ingredient, info in nutrition_info_dict.items():
        serving_size = info.get('servingSize', None)
        serving_size_unit = info.get('servingSizeUnit', '').lower()

        # scale serving size if it's available
        if serving_size and serving_size_unit == 'g':
            scale_factor = 100 / serving_size  # we scale serving size to 100g

            for nutrient_name, nutrient_info in info['nutrients'].items():
                value = nutrient_info['value'] * scale_factor  # scaling serving size to 100g
                unit = nutrient_info['unit']

                if nutrient_name in overall_nutrition:
                    overall_nutrition[nutrient_name]['value'] += value
                else:
                    overall_nutrition[nutrient_name] = {'value': value, 'unit': unit}
        else:
            print(f"Warning: Cannot scale {ingredient}; serving size is missing.")
    
    return overall_nutrition

def save_nutrition_label_as_text(overall_nutrition, filename='nutrition_facts.txt'):
    """
    Save the nutrition label in a formatted text format to a file.
    """
    formatted_output = "\n" + "=" * 100 + "\n"
    formatted_output += "Nutrition Facts for Your Recipe (Serving Size: 100g)\n"
    formatted_output += "=" * 100 + "\n"

    # display calories at the top
    if 'Energy' in overall_nutrition:
        calories = overall_nutrition['Energy']
        formatted_output += f"{'Calories':<50} {calories['value']:>8.2f} {calories['unit']}\n"
        formatted_output += "-" * 100 + "\n"
    
    # display the rest of the nutrients in a label-like format
    formatted_output += "{:<50} {:>10} {:>10}\n".format("Nutrient", "Amount per 100g", "Unit")
    formatted_output += "-" * 100 + "\n"
    for nutrient, data in overall_nutrition.items():
        if nutrient != 'Energy':  # skipping calories (calories was displayed at top)
            formatted_output += "{:<50} {:>10.2f} {:>10}\n".format(nutrient, data['value'], data['unit'])
    
    formatted_output += "=" * 100 + "\n"

    with open(filename, 'w') as f:
        f.write(formatted_output)
    print(f"Formatted nutrition facts saved to {filename}")


def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    Function to upload nutrition facts & generated recipe to the GCS bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {bucket_name}/{destination_blob_name}.")

nutrition_facts = get_nutrition_info(ingredients)
overall_nutrition = aggregate_nutrition_info_with_units(nutrition_facts)
save_nutrition_label_as_text(overall_nutrition, 'nutrition_facts.txt')
upload_to_gcs(bucket_name, 'nutrition_facts.txt', 'nutrition_facts/nutrition_facts.txt')


# Generate recipes using the fine-tuned model
finetuned_recipe = generate_recipe(finetuned_model, finetuned_tokenizer, prompt)
save_recipe_to_text(finetuned_recipe, 'generated_recipe.txt')
upload_to_gcs(bucket_name, 'generated_recipe.txt', 'generated_recipe/generated_recipe.txt')


# Print the results
# print("Fine-tuned Model Output:")
# print(finetuned_recipe)
