import json

import omegaconf
import pytest

from hermes import settings
from hermes.destinations.object_storage import ObjectStorageDestination

# TEST_PIPELINE_NAME = "sync_float_rates"
BUCKET_NAME = "a-bucket"
SOURCE_NAME = "float_rates"
TEST_SERVICE_PREFIX = settings.ObjectStorageServicesPrefixes.s3.value
SOURCE_TABLE_NAME = "dirham_change_rates"


@pytest.fixture
def mock_object_storage_config():
    """Fixture to provide a mock object storage configuration."""
    config_dict = {
        "name": "landing_zone",
        "config": {
            "bucket": BUCKET_NAME,
            "format": "json",
            "service": "s3",
        },
    }
    return omegaconf.OmegaConf.create(config_dict)


def test_object_storage_destination_init(mock_object_storage_config):
    """Test the initialization of ObjectStorageDestination."""
    destination = ObjectStorageDestination(mock_object_storage_config)
    assert destination.name == "landing_zone"
    assert destination.bucket == BUCKET_NAME
    assert destination.file_format == "json"
    assert destination.service == "s3"
    assert destination.prefix == TEST_SERVICE_PREFIX
    assert destination.format == "json"
    assert destination.data_stage == "raw"


def test_get_prefix(mock_object_storage_config):
    """Test the _get_prefix method."""
    destination = ObjectStorageDestination(mock_object_storage_config)
    assert destination._get_prefix() == TEST_SERVICE_PREFIX

    # Test with AWS S3
    mock_object_storage_config.config.service = "s3"
    destination_s3 = ObjectStorageDestination(mock_object_storage_config)
    assert destination_s3._get_prefix() == TEST_SERVICE_PREFIX


def test_get_object_path(mock_object_storage_config):
    """Test the get_object_path method."""
    destination = ObjectStorageDestination(mock_object_storage_config)
    path = destination.get_object_path(SOURCE_NAME, SOURCE_TABLE_NAME)
    expected_path = (
        f"{TEST_SERVICE_PREFIX}://{BUCKET_NAME}/{SOURCE_NAME}/{SOURCE_TABLE_NAME}.json"
    )
    assert path == expected_path


def test_load(mock_object_storage_config, mock_fsspec_open):
    """Test the load method."""
    mock_fsspec, mock_file_instance = mock_fsspec_open
    destination = ObjectStorageDestination(mock_object_storage_config)
    data = {"key": "value"}
    destination.load(SOURCE_NAME, SOURCE_TABLE_NAME, data)

    # Ensure `fsspec.open` was called at least once
    mock_fsspec.assert_called_once()
    expected_path = (
        f"{TEST_SERVICE_PREFIX}://{BUCKET_NAME}/{SOURCE_NAME}/{SOURCE_TABLE_NAME}.json"
    )
    # Extract actual call arguments
    actual_call_args, actual_call_kwargs = mock_fsspec.call_args

    # Ensure the correct file path and mode are used
    assert actual_call_kwargs["urlpath"] == expected_path
    assert actual_call_kwargs["mode"] == "w"

    # Ensure correct data was written to the file
    mock_file_instance.write.assert_called()

    # Validate the actual JSON data written
    written_data = "".join(
        call.args[0] for call in mock_file_instance.write.call_args_list
    )
    assert json.loads(written_data) == data
