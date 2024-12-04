#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi.testclient import TestClient
from unittest import mock
from api.routers.nutrition import router

client = TestClient(router)


def test_get_nutritional_info():
    with mock.patch(
        'api.routers.nutrition.get_nutrition_info'
    ) as mock_get_nutrition_info, mock.patch(
        'api.routers.nutrition.aggregate_nutrition_info_with_units'
    ) as mock_aggregate_nutrition_info:

        mock_get_nutrition_info.return_value = {
            "chicken": {"calories": 200, "protein": 10},
            "rice": {"calories": 150, "protein": 3}
        }
        mock_aggregate_nutrition_info.return_value = {
            "Protein": {"value": 0.82, "unit": "G"},
            "Total lipid (fat)": {"value": 0.31, "unit": "G"},
            "Carbohydrate, by difference": {"value": 4.04, "unit": "G"},
            "Energy": {"value": 20, "unit": "KCAL"},
            "Alcohol, ethyl": {"value": 0, "unit": "G"},
            "Water": {"value": 94.38, "unit": "G"},
            "Calcium, Ca": {"value": 0.0, "unit": "MG"}
        }

        request_payload = {"ingredients": ["chicken", "rice"]}

        response = client.post("/nutrition", json=request_payload)

        assert response.status_code == 200
        assert response.json() == {
            "nutrition_data": {
                "Protein": {"value": 0.82, "unit": "G"},
                "Total lipid (fat)": {"value": 0.31, "unit": "G"},
                "Carbohydrate, by difference": {"value": 4.04, "unit": "G"},
                "Energy": {"value": 20, "unit": "KCAL"},
                "Alcohol, ethyl": {"value": 0, "unit": "G"},
                "Water": {"value": 94.38, "unit": "G"},
                "Calcium, Ca": {"value": 0.0, "unit": "MG"}
            }
        }
