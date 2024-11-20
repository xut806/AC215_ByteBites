# src/api-service/api/routers/ocr.py
from fastapi import APIRouter, File, UploadFile
from api.utils.ner_utils import convert_ner_entities_to_list
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)
import regex as re

router = APIRouter()

# Initialize OCR and NER models
ocr_model = ocr_predictor(
    det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True
)
ocr_model.det_predictor.model.postprocessor.bin_thresh = 0.2

ner_tokenizer = AutoTokenizer.from_pretrained("Dizex/InstaFoodRoBERTa-NER")
ner_model = AutoModelForTokenClassification.from_pretrained(
    "Dizex/InstaFoodRoBERTa-NER"
)
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)


@router.post("/ocr")
async def extract_ingredients(file: UploadFile = File(...)):
    # Read the image file
    image_bytes = await file.read()
    image_array = DocumentFile.from_images(image_bytes)

    # Perform OCR
    result = ocr_model(image_array)
    text = result.render()

    # Extract words and remove numbers and special characters
    word_values = []
    for line in text.split("\n"):
        non_numeric_line = re.sub(r"\b\d+(\.\d+)?\b", "", line).strip()
        non_numeric_line = re.sub(r"[^a-zA-Z\s]", "", non_numeric_line).strip()
        if non_numeric_line:
            word_values.append(non_numeric_line)

    result_string = ", ".join(word_values)

    # Perform NER
    ner_entity_results = ner_pipeline(
        result_string, aggregation_strategy="simple"
    )
    ingredients = convert_ner_entities_to_list(
        result_string, ner_entity_results
    )

    return {"ingredients": ingredients}
