#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import os
from unittest import mock
import pytest
from fastapi.testclient import TestClient

path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path_to_src)

from api.routers.llm import router, generate_recipe  # noqa: E402

client = TestClient(router)


# fixture for mocking model and tokenizer
@pytest.fixture
def mock_model_and_tokenizer():
    mock_model = mock.Mock()
    mock_tokenizer = mock.Mock()

    mock_inputs = mock.Mock()
    mock_inputs.input_ids = [0]
    mock_tokenizer.return_value = mock_inputs

    mock_model.generate.return_value = [[0, 1, 2, 3]]
    mock_tokenizer.decode.return_value = "Generated text"

    return mock_model, mock_tokenizer


def test_generate_recipe(mock_model_and_tokenizer):
    mock_model, mock_tokenizer = mock_model_and_tokenizer

    mock_inputs = mock.Mock()
    mock_inputs.input_ids = [0]
    mock_tokenizer.return_value = mock_inputs

    mock_model.generate.return_value = [[0, 1, 2, 3]]

    mock_tokenizer.decode.return_value = (
        "Create a recipe with tomatoesGenerated text"
    )

    prompt = "Create a recipe with tomatoes"
    result = generate_recipe(mock_model, mock_tokenizer, prompt)

    print(f"Mock Model Generate Called: {mock_model.generate.call_args}")
    print(f"Mock Tokenizer Decode Called: {mock_tokenizer.decode.call_args}")
    print(f"Generated Recipe: {result}")

    assert result == "Generated text"


@mock.patch("api.routers.llm.generate_recipe")
@mock.patch("api.routers.llm.load_model_and_tokenizer")
def test_create_recipe(mock_load_model_and_tokenizer, mock_generate_recipe):
    mock_model = mock.Mock()
    mock_tokenizer = mock.Mock()
    mock_load_model_and_tokenizer.return_value = (mock_model, mock_tokenizer)

    mock_generate_recipe.return_value = "Mock Recipe"
    payload = {
        "ingredients": "tomatoes, onions",
        "dietary_preference": "vegetarian",
        "meal_type": "dinner",
        "cooking_time": 30,
    }

    response = client.post("/llm", json=payload)

    assert response.status_code == 200
    assert response.json() == {"recipe": "Mock Recipe"}
