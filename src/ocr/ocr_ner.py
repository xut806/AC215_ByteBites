import io
import json
import os
import zipfile

import regex as re
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from google.cloud import storage
from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          pipeline)

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'

# Initialize Google Cloud Storage client
client = storage.Client()

# Load the .zip receipt files from GCP bucket
bucket_name = 'recipe-dataset'
file_name = 'receipts/large-receipt-image-dataset-SRD.zip'
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)
data = blob.download_as_bytes()

def extract_images_to_temp_dir(zip_path, temp_dir='/tmp/receipts'):
    """
    extracts images from the zip file on GCP bucket to a temporary directory.
    """
    os.makedirs(temp_dir, exist_ok=True)  # Create temp directory if it doesn't exist

    with zipfile.ZipFile(io.BytesIO(zip_path), 'r') as zip_ref:
        image_files = [f for f in zip_ref.namelist() if f.lower().endswith(('.jpg', '.png'))]
        
        # extract each image to the temporary directory
        for image_file in image_files:
            zip_ref.extract(image_file, temp_dir)

    # list of extracted image paths
    return [os.path.join(temp_dir, f) for f in image_files]

image_paths = extract_images_to_temp_dir(data)

# det_arch = architecture used for text localization; for full list see https://mindee.github.io/doctr/latest/modules/models.html#doctr-models-detection
# reco_arch = architecture used for text recognition; for full list see https://mindee.github.io/doctr/latest//modules/models.html#doctr-models-recognition
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

# set a lower threshold for the text detection part so that more text region will be reognized
ocr_model.det_predictor.model.postprocessor.bin_thresh = 0.2


ner_tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_model = AutoModelForTokenClassification.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)


def parse_receipt(image_path):
    """
    takes in a path to the image directory and parses images with OCR, returning only the words (non-numerical) on the receipt
    """
    print(f"-----OCR Processing {image_path}...-----")
    image_array = DocumentFile.from_images(image_path)
    result = ocr_model(image_array)
    text = result.render()

    # extract only the words 'value' field of the JSON output (the words on the receipt)
    # and eliminate any numbers 
    word_values = []


    for line in text.split('\n'):
        non_numeric_line = re.sub(r'\b\d+(\.\d+)?\b', '', line).strip() # remove numbers
        non_numeric_line = re.sub(r'[^a-zA-Z\s]', '', non_numeric_line).strip()  # remove special characters 
        if non_numeric_line:  
            word_values.append(non_numeric_line)

    result_string = ", ".join(word_values)

    # we use the max aggregation strategy
    # so that we can use majority-vote approach to determine the final entity type
    ner_entity_results = ner_pipeline(result_string, aggregation_strategy="simple")
    return result_string, ner_entity_results

def convert_ner_entities_to_list(text, entities: list[dict]) -> list[str]:
        print("-----NER edible item recognition...-----")
        ents = []
        for ent in entities:
            e = {"start": ent["start"], "end": ent["end"], "label": ent["entity_group"]}
            if ents and -1 <= ent["start"] - ents[-1]["end"] <= 1 and ents[-1]["label"] == e["label"]:
                ents[-1]["end"] = e["end"]
                continue
            ents.append(e)

        return [text[e["start"]:e["end"]] for e in ents]


all_edible_lists = []

for image_path in image_paths:
    try:
        result_string, ner_results = parse_receipt(image_path)
        edible_list = convert_ner_entities_to_list(result_string, ner_results)
        all_edible_lists.append({"filename": image_path, "edible_items": edible_list})
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        continue

# dump OCR+NER recognized ingredients into a .json file
json_filename = "receipts_ingredients.json"
with open(json_filename, "w") as json_file:
    json.dump(all_edible_lists, json_file, indent=4)

# Upload the JSON file to GCP
output_blob_name = "receipts/receipts_ingredients.json"
blob = bucket.blob(output_blob_name)

print(f"Uploading {json_filename} to GCS as {output_blob_name}...")
blob.upload_from_filename(json_filename)
print("Upload completed successfully.")
