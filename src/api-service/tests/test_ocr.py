#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import os
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import numpy as np

path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path_to_src)


@pytest.fixture
def mock_dependencies():
    with patch("doctr.io.DocumentFile.from_images") as mock_from_images, patch(
        "doctr.models.ocr_predictor"
    ) as mock_ocr_predictor, patch(
        "api.routers.ocr.pipeline"
    ) as mock_pipeline:
        mock_from_images.return_value = [
            np.zeros((100, 100, 3), dtype=np.uint8)
        ]

        mock_ocr_result = Mock()
        mock_ocr_result.render.return_value = "ingredient1\ningredient2"
        mock_ocr_model = Mock(return_value=mock_ocr_result)
        mock_ocr_predictor.return_value = mock_ocr_model

        mock_pipeline.return_value = [
            {"entity_group": "ingredient", "start": 0, "end": 11},
            {"entity_group": "ingredient", "start": 12, "end": 23},
        ]

        yield


@pytest.fixture
def test_client():
    from api.routers.ocr import router

    return TestClient(router)


def test_ocr_extract_ingredients(mock_dependencies, test_client):
    response = test_client.post(
        "/ocr",
        files={"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")},
    )

    print("Response JSON:", response.json())

    assert response.status_code == 200
