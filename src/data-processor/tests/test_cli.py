#!/usr/bin/env python3

import os
import sys
import pandas as pd
from unittest import mock

path_to_cli = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path_to_cli)

import cli  # noqa: E402


def test_download_data_from_gcs(mocker):
    mock_client = mocker.patch('cli.storage.Client')
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    test_data = pd.DataFrame({
        'prompt': ['test prompt'],
        'completion': ['test completion']
    })
    mock_blob.download_as_bytes.return_value = test_data.to_json(
        orient='records',
        lines=True).encode()

    mock_client.return_value.get_bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    result = cli.download_data_from_gcs('test_bucket', 'test_file.jsonl')

    mock_client.assert_called_once()
    mock_client.return_value.get_bucket.assert_called_once_with('test_bucket')
    mock_bucket.blob.assert_called_once_with('test_file.jsonl')
    mock_blob.download_as_bytes.assert_called_once()
    assert isinstance(result, pd.DataFrame)


def test_clean_data():
    test_data = pd.DataFrame({
        'prompt': ['old text here. more text', 'old text here. other text'],
        'completion': ['completion1', 'completion2']
    })

    result = cli.clean_data(test_data, 'old text here', 'new text')

    assert all(result['prompt'].str.contains('new text'))
    assert not any(result['prompt'].str.contains('old text here'))


def test_filter_data():
    test_data = pd.DataFrame({
        'prompt': ['short prompt', 'x' * 500],
        'completion': ['short completion', 'x' * 3000]
    })

    result = cli.filter_data(test_data)

    assert len(result) == 1
    assert result.iloc[0]['prompt'] == 'short prompt'
    assert result.iloc[0]['completion'] == 'short completion'


def test_upload_to_gcp(mocker):
    mock_client = mocker.patch('cli.storage.Client')
    mock_bucket = mock.Mock()
    mock_blob = mock.Mock()

    mock_client.return_value.get_bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    test_data = pd.DataFrame({
        'prompt': ['test prompt'],
        'completion': ['test completion']
    })

    cli.upload_to_gcp(test_data, 'test_bucket', 'test_destination_blob')

    mock_client.assert_called_once()
    mock_client.return_value.get_bucket.assert_called_once_with('test_bucket')
    mock_bucket.blob.assert_called_once_with('test_destination_blob')
    mock_blob.upload_from_string.assert_called_once()


def test_formatting_prompt():
    test_data = {
        'prompt': ['make pizza'],
        'completion': ['1. Make dough 2. Add toppings']
    }

    result = cli.formatting_prompt(test_data)

    assert isinstance(result, dict)
    assert 'text' in result
    assert len(result['text']) == 1
    assert 'make pizza' in result['text'][0]
    assert '1. Make dough 2. Add toppings' in result['text'][0]
    assert '<|end_of_text|>' in result['text'][0]


def test_main(mocker):
    # Mock all the main dependencies
    mock_download = mocker.patch('cli.download_data_from_gcs')
    mock_upload = mocker.patch('cli.upload_to_gcp')
    mock_dataset = mocker.patch('cli.Dataset')

    test_data = pd.DataFrame({
        'prompt': ['test prompt'],
        'completion': ['test completion']
    })
    mock_download.return_value = test_data

    mock_split = mock.Mock()
    mock_split.values.return_value = (mock.Mock(), mock.Mock())
    mock_dataset.from_pandas.return_value \
        .train_test_split.return_value = mock_split

    cli.main()

    mock_download.assert_called_once()
    assert mock_upload.call_count == 3
    mock_dataset.from_pandas.assert_called_once()
