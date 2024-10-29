from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from google.cloud import storage
import json
import regex as re
import os
import zipfile
import io
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

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

with zipfile.ZipFile(io.BytesIO(data), 'r') as zip_ref:
    receipt_files = zip_ref.namelist()  # List all files in the ZIP archive
    extracted_files = {name: zip_ref.read(name) for name in receipt_files if name.lower().endswith(('.jpg', '.png'))}


# det_arch = architecture used for text localization; for full list see https://mindee.github.io/doctr/latest/modules/models.html#doctr-models-detection
# reco_arch = architecture used for text recognition; for full list see https://mindee.github.io/doctr/latest//modules/models.html#doctr-models-recognition
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

ner_tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_model = AutoModelForTokenClassification.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)


def parse_receipt(single_img_doc):
    result = ocr_model(single_img_doc)
    json_output = result.export()

    # extract only the words 'value' field of the JSON output (the words on the receipt)
    # and eliminate any numbers 
    word_values = []

    for page in json_output['pages']:
        for block in page['blocks']:
            for line in block.get('lines', []):
                for word in line.get('words', []):
                    if re.match("^[A-Za-z]+$", word['value']):
                        word_values.append(word['value'])

    result_string = ", ".join(word_values)
    ner_entity_results = ner_pipeline(result_string, aggregation_strategy="simple")
    return result_string, ner_entity_results

def convert_ner_entities_to_list(text, entities: list[dict]) -> list[str]:
        ents = []
        for ent in entities:
            e = {"start": ent["start"], "end": ent["end"], "label": ent["entity_group"]}
            if ents and -1 <= ent["start"] - ents[-1]["end"] <= 1 and ents[-1]["label"] == e["label"]:
                ents[-1]["end"] = e["end"]
                continue
            ents.append(e)

        return [text[e["start"]:e["end"]] for e in ents]

all_edible_lists = []

for filename, image_bytes in extracted_files.items():
    print(f"Processing: {filename}")
    result_string, ner_results = parse_receipt(image_bytes)
    edible_list = convert_ner_entities_to_list(result_string, ner_results)
    all_edible_lists.append({"filename": filename, "edible_items": edible_list})

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