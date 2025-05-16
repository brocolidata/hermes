import json

import pytest
from botocore.exceptions import BotoCoreError

import hermes

TEST_PIPELINE_NAME = "sync_float_rates"
SOURCE_NAME = "float_rates"
SOURCE_TABLE_NAME = "dirham_change_rates"


@pytest.fixture
def set_config_for_object_storage(monkeypatch, test_folder):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv(
        "HERMES_ARTIFACTS_FOLDER",
        f"{test_folder}/assets/artifacts/object_storage",
    )
    yield


def test_object_storage(
    set_config_for_object_storage,
    set_aws_env_vars,
    mock_custom_source_extract,
    mock_fsspec_open,
    get_dirham_change_rates_data,
):
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline.run()

    # Assert successes are recorded in the Pipeline object
    SUCCESSES = [
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "landing_zone",
        }
    ]
    assert pipeline.successes == SUCCESSES

    mock_fsspec, mock_file_instance = mock_fsspec_open  # Unpack fixture

    # Ensure `fsspec.open` was called at least once
    mock_fsspec.assert_called_once()

    # Extract actual call arguments
    actual_call_args, actual_call_kwargs = mock_fsspec.call_args

    # Ensure the correct file path and mode are used
    expected_file_path_start = f"s3://a-bucket/{SOURCE_NAME}/{SOURCE_TABLE_NAME}/{SOURCE_TABLE_NAME}_"  # Adjust as needed
    assert actual_call_kwargs["urlpath"].startswith(expected_file_path_start)
    assert actual_call_kwargs["mode"] == "w"

    # Ensure correct data was written to the file
    mock_file_instance.write.assert_called()

    # Validate the actual JSON data written
    written_data = "".join(
        call.args[0] for call in mock_file_instance.write.call_args_list
    )
    assert json.loads(written_data) == get_dirham_change_rates_data


def test_object_storage_exception(
    set_config_for_object_storage,
    set_aws_env_vars,
    mock_custom_source_extract,
    mock_fsspec_open,
    get_dirham_change_rates_data,
):
    mocked_open, _ = mock_fsspec_open
    mocked_open.side_effect = BotoCoreError
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline.run()
    ERRORS = [
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "landing_zone",
            "error_type": "ObjectStorageDestinationError",
            "error_message": "Object Storage: error while loading data to landing_zone, located at s3://a-bucket/float_rates/dirham_change_rates/dirham_change_rates_04_12_2025_12_42_33.json.\n            error : An unspecified error occurred\n        ",
        }
    ]
    assert pipeline.errors[0]["source_name"] == ERRORS[0]["source_name"]
    assert pipeline.errors[0]["source_table_name"] == ERRORS[0]["source_table_name"]
    assert pipeline.errors[0]["destination_name"] == ERRORS[0]["destination_name"]
    assert pipeline.errors[0]["error_type"] == ERRORS[0]["error_type"]
    # assert pipeline.errors == ERRORS
