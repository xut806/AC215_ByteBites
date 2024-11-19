import pytest
from unittest import mock
from io import StringIO
import sys
import os

path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, path_to_src)

from inference_nutrition import (
    generate_recipe,
    save_recipe_to_text,
    get_nutrition_info,
    aggregate_nutrition_info_with_units,
    save_nutrition_label_as_text,
    upload_to_gcs,
)

# Mocking the storage client
@pytest.fixture
def mock_storage_client():
    with mock.patch('inference_nutrition.storage.Client', autospec=True) as mock_client:
        yield mock_client

def test_generate_recipe_empty_prompt():
    mock_model = mock.Mock()
    mock_tokenizer = mock.Mock()

    # mock return value that behaves like the actual return of tokenizer()
    mock_inputs = mock.Mock()
    mock_inputs.input_ids = [0]
    
    # set the return value of the tokenizer to the mock object
    mock_tokenizer.return_value = mock_inputs
    mock_model.generate.return_value = [[0, 1, 2, 3]]
    mock_tokenizer.decode.return_value = "Generated text"

    prompt = ""
    result = generate_recipe(mock_model, mock_tokenizer, prompt)

    assert result == "Generated text"

@mock.patch("builtins.open", side_effect=IOError("File error"))
def test_save_recipe_to_text_file_error(mock_open):
    with pytest.raises(IOError, match="File error"):
        save_recipe_to_text("Test recipe", "invalid_path.txt")

@mock.patch('inference_nutrition.requests.get')
def test_get_nutrition_info_api_failure(mock_get):
    mock_get.return_value.status_code = 500
    nutrition_info = get_nutrition_info(["tomato"])
    # expect an empty result on failure
    assert nutrition_info == {}

@mock.patch('inference_nutrition.requests.get')
def test_get_nutrition_info_no_foods(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"foods": []}
    nutrition_info = get_nutrition_info(["unknown_ingredient"])
    # expect empty result for unknown ingredients
    assert nutrition_info == {}

def test_aggregate_nutrition_info_with_missing_serving_size():
    input_data = {
        "tomato": {
            "servingSize": None,
            "servingSizeUnit": "g",
            "nutrients": {
                "Energy": {"value": 18, "unit": "kcal"},
                "Protein": {"value": 0.9, "unit": "g"},
            },
        }
    }
    result = aggregate_nutrition_info_with_units(input_data)
    # expect an empty result if serving size is missing
    assert result == {}