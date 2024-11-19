import pytest
from unittest import mock
import sys
import os
path_to_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
print(f"Adding path to sys.path: {path_to_src}")
sys.path.insert(0, path_to_src)

from upload import upload_weights_to_gcs
@pytest.fixture(autouse=True)
def mock_google_cloud_client():
    with mock.patch('upload.storage.Client', autospec=True) as mock_client:
        yield mock_client

@pytest.fixture(autouse=True)
def mock_env_var():
    # mock the environment variable
    with mock.patch.dict('os.environ', {"GOOGLE_APPLICATION_CREDENTIALS": "/mock/path/to/recipe.json"}, clear=True):
        yield

@pytest.fixture
def mock_print():
    with mock.patch('builtins.print') as mocked_print:
        yield mocked_print

def test_upload_weights_to_gcs(mock_google_cloud_client, mock_print):
    # set up mock objects
    mock_client_instance = mock_google_cloud_client.return_value
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()

    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    source_file = "/path/to/mock_model.safetensors"
    destination_blob_name = "mock_model/model.safetensors"
    bucket_name = "test-bucket"
    
    upload_weights_to_gcs(bucket_name, source_file, destination_blob_name)

    mock_google_cloud_client.assert_called_once()
    mock_client_instance.bucket.assert_called_once_with(bucket_name)
    mock_bucket.blob.assert_called_once_with(destination_blob_name)
    mock_blob.upload_from_filename.assert_called_once_with(source_file)

    mock_print.assert_called_once_with(
        f"Successfully Uploaded {source_file} to {destination_blob_name}"
    )