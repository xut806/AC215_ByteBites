#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.utils.nutrition_utils import get_nutrition_info, \
    aggregate_nutrition_info_with_units


class TestNutritionUtils(unittest.TestCase):

    @patch('api.utils.nutrition_utils.requests.get')
    def test_get_nutrition_info_success(self, mock_get):
        # Mock response data
        mock_response = {
            "foods": [
                {
                    "description": "Chicken, raw",
                    "dataType": "Survey (FNDDS)",
                    "servingSize": 100,
                    "servingSizeUnit": "g",
                    "foodNutrients": [
                        {
                            "nutrientName": "Protein",
                            "value": 27,
                            "unitName": "G"
                        },
                        {
                            "nutrientName": "Energy",
                            "value": 239,
                            "unitName": "KCAL"
                        }
                    ]
                }
            ]
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = get_nutrition_info(['chicken'])

        expected_result = {
            'chicken': {
                'description': 'Chicken, raw',
                'dataType': 'Survey (FNDDS)',
                'servingSize': 100,
                'servingSizeUnit': 'g',
                'nutrients': {
                    'Protein': {'value': 27, 'unit': 'G'},
                    'Energy': {'value': 239, 'unit': 'KCAL'}
                }
            }
        }
        self.assertEqual(result, expected_result)

    @patch('api.utils.nutrition_utils.requests.get')
    def test_get_nutrition_info_no_data(self, mock_get):
        mock_response = {"foods": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = get_nutrition_info(['unknown_ingredient'])

        self.assertEqual(result, {})

    def test_aggregate_nutrition_info_with_units(self):
        nutrition_info_dict = {
            'chicken': {
                'description': 'Chicken, raw',
                'dataType': 'Survey (FNDDS)',
                'servingSize': 100,
                'servingSizeUnit': 'g',
                'nutrients': {
                    'Protein': {'value': 27, 'unit': 'G'},
                    'Energy': {'value': 239, 'unit': 'KCAL'}
                }
            },
            'rice': {
                'description': 'Rice, white, raw',
                'dataType': 'Survey (FNDDS)',
                'servingSize': 100,
                'servingSizeUnit': 'g',
                'nutrients': {
                    'Protein': {'value': 2.7, 'unit': 'G'},
                    'Energy': {'value': 130, 'unit': 'KCAL'}
                }
            }
        }

        result = aggregate_nutrition_info_with_units(nutrition_info_dict)

        expected_result = {
            'Protein': {'value': 29.7, 'unit': 'G'},
            'Energy': {'value': 369, 'unit': 'KCAL'}
        }

        self.assertEqual(result, expected_result)

    def test_aggregate_nutrition_info_missing_serving_size(self):
        nutrition_info_dict = {
            'unknown': {
                'description': 'Unknown ingredient',
                'dataType': 'Survey (FNDDS)',
                'servingSize': None,
                'servingSizeUnit': '',
                'nutrients': {
                    'Protein': {'value': 0, 'unit': 'G'},
                    'Energy': {'value': 0, 'unit': 'KCAL'}
                }
            }
        }

        result = aggregate_nutrition_info_with_units(nutrition_info_dict)

        expected_result = {}

        self.assertEqual(result, expected_result)

    @patch('api.utils.nutrition_utils.requests.get')
    def test_get_nutrition_info_no_foods(self, mock_get):
        mock_response = {"foods": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = get_nutrition_info(['unknown_ingredient'])
        self.assertEqual(result, {})

    @patch('api.utils.nutrition_utils.requests.get')
    def test_get_nutrition_info_missing_serving_size(self, mock_get):
        mock_response = {
            "foods": [
                {
                    "description": "Ingredient with no serving size",
                    "dataType": "Survey (FNDDS)",
                    "servingSize": None,
                    "servingSizeUnit": None,
                    "foodNutrients": [
                        {
                            "nutrientName": "Protein",
                            "value": 10,
                            "unitName": "G"
                        }
                    ]
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = get_nutrition_info(['ingredient_with_no_serving_size'])
        expected_result = {
            'ingredient_with_no_serving_size': {
                'description': 'Ingredient with no serving size',
                'dataType': 'Survey (FNDDS)',
                'servingSize': 100,
                'servingSizeUnit': 'g',
                'nutrients': {
                    'Protein': {'value': 10, 'unit': 'G'}
                }
            }
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
