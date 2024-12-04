#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import ssl
from unittest.mock import patch, Mock
import sys
import os
import pytest
from fastapi.testclient import TestClient
import numpy as np

# disable SSL certificate verification which arises from doctr
ssl._create_default_https_context = ssl._create_unverified_context

path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path_to_src)

from api.service import app  # noqa: E402

client = TestClient(app)


# mock dependencies
@pytest.fixture
def mock_dependencies():
    with patch("doctr.io.DocumentFile.from_images") as mock_from_images, patch(
        "doctr.models.ocr_predictor"
    ) as mock_ocr_predictor, patch(
        "api.routers.ocr.pipeline"
    ) as mock_pipeline, patch(
        "api.routers.llm.load_model_and_tokenizer"
    ) as mock_load_model_and_tokenizer, patch(
        "api.routers.llm.generate_recipe"
    ) as mock_generate_recipe:
        mock_from_images.return_value = [
            np.zeros((100, 100, 3), dtype=np.uint8)
        ]

        mock_ocr_result = Mock()
        mock_ocr_result.render.return_value = "ingredient1\ningredient2"
        mock_ocr_predictor.return_value = mock_ocr_result

        mock_pipeline.return_value = [
            {"entity_group": "ingredient", "start": 0, "end": 11},
            {"entity_group": "ingredient", "start": 12, "end": 23},
        ]

        mock_load_model_and_tokenizer.return_value = (Mock(), Mock())
        mock_generate_recipe.return_value = "Mock Recipe"

        yield


# integration test: For integrating multiple components.
@pytest.mark.usefixtures("mock_dependencies")
def test_service_integration():
    # OCR endpoint
    ocr_response = client.post(
        "/api/ocr",
        files={"file": ("test_image.jpg", b"valid_image_data", "image/jpeg")},
    )

    print("OCR Response JSON:", ocr_response.json())
    assert ocr_response.status_code == 200
    assert "ingredients" in ocr_response.json() 

    # LLM endpoint
    llm_payload = {
        "ingredients": "ingredient1, ingredient2",
        "dietary_preference": "vegetarian",
        "meal_type": "dinner",
        "cooking_time": 30,
    }
    llm_response = client.post("/api/llm", json=llm_payload)

    print("LLM Response JSON:", llm_response.json())
    assert llm_response.status_code == 200
    assert "recipe" in llm_response.json() 

    # Nutrition endpoint
    nutrition_payload = {
        "ingredients": ["ingredient1", "ingredient2"],
    }
    nutrition_response = client.post("/api/nutrition", json=nutrition_payload)

    print("Nutrition Response JSON:", nutrition_response.json())
    assert nutrition_response.status_code == 200
    assert "nutrition_data" in nutrition_response.json() 


# System test
@pytest.mark.usefixtures("mock_dependencies")
def test_system_end_to_end():
    """System test for the entire service: OCR -> LLM -> Nutrition."""

    # Mocked file data
    fake_image_data = b"fake_image_data"

    # Test OCR endpoint
    ocr_response = client.post(
        "/api/ocr",
        files={"file": ("test_image.jpg", fake_image_data, "image/jpeg")},
    )

    print("OCR Response JSON:", ocr_response.json())
    assert ocr_response.status_code == 200
    ingredients = ocr_response.json().get("ingredients")
    assert ingredients is not None

    # Use OCR output as input for the LLM endpoint
    llm_payload = {
        "ingredients": ", ".join(ingredients),
        "dietary_preference": "vegetarian",
        "meal_type": "dinner",
        "cooking_time": 30,
    }
    llm_response = client.post("/api/llm", json=llm_payload)

    print("LLM Response JSON:", llm_response.json())
    assert llm_response.status_code == 200
    assert "recipe" in llm_response.json()

    # Use OCR output as input for the Nutrition endpoint
    nutrition_payload = {
        "ingredients": ingredients,
    }
    nutrition_response = client.post("/api/nutrition", json=nutrition_payload)

    print("Nutrition Response JSON:", nutrition_response.json())
    assert nutrition_response.status_code == 200
    assert "nutrition_data" in nutrition_response.json()
