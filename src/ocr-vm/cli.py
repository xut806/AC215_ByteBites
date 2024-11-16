from fastapi import FastAPI, UploadFile, File, HTTPException
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from fastapi.middleware.cors import CORSMiddleware
import regex as re
import os
import uvicorn
import json
import logging
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OCR and NER models
logger.info("Loading OCR model...")
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
ocr_model.det_predictor.model.postprocessor.bin_thresh = 0.2

logger.info("Loading NER model...")
ner_tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_model = AutoModelForTokenClassification.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)

logger.info("Models loaded successfully.")

@app.post("/ocr_ner/")
async def process_image(file: UploadFile = File(...)):
    try:
        # Read the uploaded image file
        image_bytes = await file.read()
        logger.info(f"Processing OCR for image")
        image = DocumentFile.from_images(io.BytesIO(image_bytes))

        # Run OCR
        ocr_result = ocr_model(image)
        text = ocr_result.render()
        logger.info("OCR processing completed successfully.")

        # extract only the words 'value' field of the JSON output (the words on the receipt)
        # and eliminate any numbers 
        word_values = []


        for line in text.split('\n'):
            non_numeric_line = re.sub(r'\b\d+(\.\d+)?\b', '', line).strip() # remove numbers
            non_numeric_line = re.sub(r'[^a-zA-Z\s]', '', non_numeric_line).strip()  # remove special characters 
            if non_numeric_line:  
                word_values.append(non_numeric_line)

        result_string = ", ".join(word_values)

        # Run NER on the recognized text
        ner_results = ner_pipeline(result_string, aggregation_strategy="simple")

        # convert NER entities to list
        ents = []
        for ent in ner_results:
            e = {"start": ent["start"], "end": ent["end"], "label": ent["entity_group"]}
            if ents and -1 <= ent["start"] - ents[-1]["end"] <= 1 and ents[-1]["label"] == e["label"]:
                ents[-1]["end"] = e["end"]
                continue
            ents.append(e)

        logger.info("NER processing completed successfully.")

        # return {"recognized_text": result_string, "ner_results": ner_results}
        return [text[e["start"]:e["end"]] for e in ents]

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the image")


@app.get("/health")
async def health():
    """Health check endpoint to confirm service is running"""
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
