#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import os
path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path_to_src)

import pytest  # noqa: E402
from unittest import mock  # noqa: E402

from inference_nutrition import (  # noqa: E402
    # generate_recipe,
    save_recipe_to_text,
    get_nutrition_info,
    aggregate_nutrition_info_with_units,
    save_nutrition_label_as_text,
    upload_to_gcs,
)


# Mocking the storage client
@pytest.fixture
def mock_storage_client():
    with mock.patch(
        "inference_nutrition.storage.Client", autospec=True
    ) as mock_client:
        yield mock_client


# def test_generate_recipe_empty_prompt():
#     mock_model = mock.Mock()
#     mock_tokenizer = mock.Mock()

#     # mock return value that behaves like the actual return of tokenizer()
#     mock_inputs = mock.Mock()
#     mock_inputs.input_ids = [0]

#     # set the return value of the tokenizer to the mock object
#     mock_tokenizer.return_value = mock_inputs
#     mock_model.generate.return_value = [[0, 1, 2, 3]]
#     mock_tokenizer.decode.return_value = "Generated text"

#     prompt = ""
#     result = generate_recipe(mock_model, mock_tokenizer, prompt)

#     assert result == "Generated text"


@mock.patch("builtins.open", side_effect=IOError("File error"))
def test_save_recipe_to_text_file_error(mock_open):
    with pytest.raises(IOError, match="File error"):
        save_recipe_to_text("Test recipe", "invalid_path.txt")


@mock.patch("inference_nutrition.requests.get")
def test_get_nutrition_info_api_failure(mock_get):
    mock_get.return_value.status_code = 500
    nutrition_info = get_nutrition_info(["tomato"])
    # expect an empty result on failure
    assert nutrition_info == {}


@mock.patch("inference_nutrition.requests.get")
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


@mock.patch("builtins.open", new_callable=mock.mock_open)
def test_save_nutrition_label_as_text(mock_open):
    nutrition_data = {
        "Energy": {"value": 200, "unit": "kcal"},
        "Protein": {"value": 10, "unit": "g"},
        "Carbohydrates": {"value": 30, "unit": "g"}
    }
    test_file_path = "test_nutrition.txt"
    save_nutrition_label_as_text(nutrition_data, test_file_path)

    mock_open.assert_called_once_with(test_file_path, "w")
    handle = mock_open()

    print("Actual written content:")
    for call in handle.write.call_args_list:
        print(call)

    written_content = "".join(
        call.args[0] for call in handle.write.call_args_list)
    assert (
        "Nutrition Facts for Your Recipe (Serving Size: 100g)"
        in written_content
    )
    assert "Calories" in written_content
    assert "200.00 kcal" in written_content
    assert "Protein" in written_content
    assert "10.00          g" in written_content


@mock.patch("inference_nutrition.storage.Client", autospec=True)
def test_upload_to_gcs(mock_storage_client):
    mock_client_instance = mock_storage_client.return_value
    mock_bucket = mock_client_instance.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    bucket_name = "test-bucket"
    source_file_name = "test_file.txt"
    destination_blob_name = "path/to/test_file.txt"

    upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
    mock_storage_client.assert_called_once()
    mock_client_instance.bucket.assert_called_once_with(bucket_name)
    mock_bucket.blob.assert_called_once_with(destination_blob_name)
    mock_blob.upload_from_filename.assert_called_once_with(source_file_name)
