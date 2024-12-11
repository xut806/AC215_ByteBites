#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
from unittest import mock

path_to_cli = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path_to_cli)

import cli  # noqa: E402


def test_upload_to_gcp(mocker):
    mock_client = mocker.patch('cli.storage.Client')
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    mock_client.return_value.get_bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)

    data_path = 'test_data.jsonl'
    bucket_name = 'test_bucket'
    destination_blob_name = 'test_destination_blob'

    cli.upload_to_gcp(data_path, bucket_name, destination_blob_name)

    mock_client.assert_called_once()
    mock_client.return_value.get_bucket.assert_called_once_with(bucket_name)
    mock_bucket.blob.assert_called_once_with(destination_blob_name)
    mock_blob.upload_from_file.assert_called_once_with(
        mock_open.return_value, content_type="application/json"
    )


def test_main(mocker):
    mock_upload = mocker.patch('cli.upload_to_gcp')

    cli.main()

    mock_upload.assert_called_once_with(
        'dataset/recipe_prompts_test.jsonl',
        'ai-recipe-data',
        'raw/recipe_prompts_test.jsonl'
    )
