from google.cloud import storage
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json
import regex as re
import tempfile
import os
import io
from zipfile import ZipFile

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'

def download_from_gcs(bucket_name, source_blob_name, local_path):
    """Downloads a blob from GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(local_path)

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

def convert_entities_to_list(text, entities):
    """Converts NER entities to a list of ingredients."""
    ents = []
    for ent in entities:
        e = {"start": ent["start"], "end": ent["end"], "label": ent["entity_group"]}
        if ents and -1 <= ent["start"] - ents[-1]["end"] <= 1 and ents[-1]["label"] == e["label"]:
            ents[-1]["end"] = e["end"]
            continue
        ents.append(e)
    return [text[e["start"]:e["end"]] for e in ents]

def process_image(local_image_path):
    """Process a single image and return ingredients."""
    # Initialize OCR model
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    
    # Load and process image
    doc = DocumentFile.from_images(local_image_path)
    result = ocr_model(doc)
    
    # Extract words
    json_output = result.export()
    word_values = []
    
    for page in json_output['pages']:
        for block in page['blocks']:
            for line in block.get('lines', []):
                for word in line.get('words', []):
                    if re.match("^[A-Za-z]+$", word['value']):
                        word_values.append(word['value'])
    
    result_string = ", ".join(word_values)
    
    # Initialize NER model
    tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
    ner_model = AutoModelForTokenClassification.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
    pipe = pipeline("ner", model=ner_model, tokenizer=tokenizer, aggregation_strategy="simple")
    
    # Process with NER
    ner_results = pipe(result_string)
    ingredients = convert_entities_to_list(result_string, ner_results)
    
    return {
        'raw_text': result_string,
        'ingredients': ingredients
    }

def verify_results(bucket_name, output_filename):
    """Verify the results file was created and contains valid data."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(output_filename)
        
        # Check if file exists
        if not blob.exists():
            return False
            
        # Download and verify JSON content
        json_data = json.loads(blob.download_as_string())
        
        if not isinstance(json_data, list):
            return False
            
        return True
        
    except Exception as e:
        return False

def validate_zip_file(zip_data):
    """Validates if the zip file is readable and contains valid images."""
    try:
        with io.BytesIO(zip_data) as zip_buffer:
            # Check if it's a valid zip file
            if not zip_buffer.getvalue().startswith(b'PK'):
                return False
                
            with ZipFile(zip_buffer, 'r') as zip_file:
                # Check if zip file can be opened
                if zip_file.testzip() is not None:
                    return False
                
                # Check for image files
                image_files = [f for f in zip_file.filelist 
                             if f.filename.lower().endswith(('.png', '.jpg', '.jpeg'))
                             and not f.filename.startswith('__MACOSX/')
                             and not f.filename.startswith('._')]
                
                if not image_files:
                    return False
                
                # Try reading first image to verify accessibility
                try:
                    with zip_file.open(image_files[0].filename) as test_image:
                        test_data = test_image.read()
                        if not test_data:
                            return False
                except Exception:
                    return False
                
        return True
        
    except Exception:
        return False

def main():
    # Configuration
    bucket_name = 'recipe-dataset'
    file_name = 'receipts/small-receipt-image-dataset-SRD.zip'
    output_filename = 'receipts/receipts_ingredients.json'
    
    # Initialize Google Cloud Storage client
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    
    # Download the zip file
    blob = bucket.blob(file_name)
    zip_data = blob.download_as_bytes()
    
    # Validate zip file before processing
    if not validate_zip_file(zip_data):
        return
        
    # Store all results
    all_results = []
    
    # Process zip file in memory
    with io.BytesIO(zip_data) as zip_buffer:
        with ZipFile(zip_buffer, 'r') as zip_file:
            # List all files in zip
            image_files = [f for f in zip_file.filelist 
                         if f.filename.lower().endswith(('.png', '.jpg', '.jpeg'))
                         and not f.filename.startswith('__MACOSX/')
                         and not f.filename.startswith('._')]
            
            processed_files = 0
            failed_files = 0
            
            # Process each image in the zip
            for file_info in image_files:
                processed_files += 1
                
                # Extract image to temporary file
                with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_info.filename)[1]) as temp_image:
                    with zip_file.open(file_info.filename) as image_file:
                        temp_image.write(image_file.read())
                        temp_image.flush()
                    
                    try:
                        # Process image
                        results = process_image(temp_image.name)
                        
                        # Add filename to results
                        results['filename'] = file_info.filename
                        all_results.append(results)
                    except Exception:
                        failed_files += 1
                        continue
            
            # Save all results to a single temporary JSON file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as temp_json:
                json.dump(all_results, temp_json, indent=4)
                temp_json.flush()
                
                # Upload single results file to GCS
                upload_to_gcs(bucket_name, temp_json.name, output_filename)
                print(f"Results uploaded to gs://{bucket_name}/{output_filename}")
    
    # Verify results at the end
    if not verify_results(bucket_name, output_filename):
        print("Script completed with errors!")

if __name__ == "__main__":
    main()
