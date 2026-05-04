import json
from unittest.mock import patch

import omegaconf
import pytest
from generic_object_storage_destination.exceptions import ObjectStorageDestinationError
from local_storage_destination.connector import LocalStorageDestination

BUCKET_NAME = "a-local-bucket"
SOURCE_NAME = "local_files"
TEST_SERVICE_PREFIX = ""
SOURCE_TABLE_NAME = "my_documents"


@pytest.fixture
def mock_local_storage_config():
    """Fixture to provide a mock local storage configuration."""
    config_dict = {
        "name": "local_landing_zone",
        "config": {
            "bucket": BUCKET_NAME,
            "format": "json",
            "service": "local_storage",
        },
    }
    return omegaconf.OmegaConf.create(config_dict)


def test_local_storage_destination_init(mock_local_storage_config):
    """Test the initialization of LocalStorageDestination."""
    destination = LocalStorageDestination(mock_local_storage_config)
    assert destination.name == "local_landing_zone"
    assert destination.bucket == BUCKET_NAME
    assert destination.prefix == TEST_SERVICE_PREFIX
    assert destination.format == "json"
    assert destination.data_stage == "raw"


def test_get_prefix(mock_local_storage_config):
    """Test the _get_prefix method."""
    destination = LocalStorageDestination(mock_local_storage_config)
    assert destination.prefix == TEST_SERVICE_PREFIX


def test_get_object_path(mock_local_storage_config):
    """Test the get_object_path method."""
    destination = LocalStorageDestination(mock_local_storage_config)
    path = destination.get_object_path(SOURCE_NAME, SOURCE_TABLE_NAME)
    expected_path_start = f"{TEST_SERVICE_PREFIX}/{BUCKET_NAME}/{SOURCE_NAME}/{SOURCE_TABLE_NAME}/{SOURCE_TABLE_NAME}_"
    assert path.startswith(expected_path_start)


def test_load(mock_local_storage_config, mock_fsspec_open):
    """Test the load method."""
    mock_fsspec, mock_file_instance = mock_fsspec_open
    destination = LocalStorageDestination(mock_local_storage_config)
    data = {"doc_id": 123, "content": "This is a test document."}
    destination.load(SOURCE_NAME, SOURCE_TABLE_NAME, data)

    # Ensure `fsspec.open` was called at least once
    mock_fsspec.assert_called_once()
    expected_path_start = f"{TEST_SERVICE_PREFIX}/{BUCKET_NAME}/{SOURCE_NAME}/{SOURCE_TABLE_NAME}/{SOURCE_TABLE_NAME}_"
    # Extract actual call arguments
    actual_call_args, actual_call_kwargs = mock_fsspec.call_args

    # Ensure the correct file path and mode are used
    assert actual_call_kwargs["urlpath"].startswith(expected_path_start)
    assert actual_call_kwargs["mode"] == "w"

    # Ensure correct data was written to the file
    mock_file_instance.write.assert_called()

    # Validate the actual JSON data written
    written_data = "".join(
        call.args[0] for call in mock_file_instance.write.call_args_list
    )
    assert json.loads(written_data) == data


@patch("fsspec.open", side_effect=Exception("Filesystem error"))
def test_load_object_storage_exception(mock_fsspec_open, mock_local_storage_config):
    """Test that LocalStorageDestination.load raises an exception on fsspec error."""
    destination = LocalStorageDestination(mock_local_storage_config)
    data = {"key": "value"}
    with pytest.raises(ObjectStorageDestinationError):
        destination.load("test_source", "test_table", data)

    mock_fsspec_open.assert_called_once()
