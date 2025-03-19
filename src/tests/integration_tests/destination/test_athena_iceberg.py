import pandas as pd
import pytest
from botocore.exceptions import BotoCoreError

import hermes
import hermes.pipeline

TEST_PIPELINE_NAME = "sync_float_rates"
SOURCE_NAME = "float_rates"
SOURCE_TABLE_NAME = "dirham_change_rates"


@pytest.fixture
def set_config_for_athena_iceberg(monkeypatch, test_folder):
    """Fixture to set environment variables for tests."""

    monkeypatch.setenv(
        # "HERMES_CONFIG_FOLDER", "tests/assets/config/test_athena_iceberg"
        "HERMES_CONFIG_FOLDER",
        f"{test_folder}/assets/config/test_athena_iceberg",
    )
    yield


def test_athena_iceberg(
    # set_hermes_config_folder,
    set_config_for_athena_iceberg,
    set_aws_env_vars,
    mock_athena_to_iceberg,
    mock_custom_source_extract,
    get_processed_float_rates_test_data,
):
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline.run()

    # Assert successes are recorded in the Pipeline object
    SUCCESSES = [
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "demo_athena_iceberg",
        }
    ]
    assert pipeline.successes == SUCCESSES

    # Ensure function was called once
    mock_athena_to_iceberg.assert_called_once()

    # Extract the actual call arguments
    actual_call_args = mock_athena_to_iceberg.call_args.kwargs

    # Compare DataFrame separately
    expected_df = get_processed_float_rates_test_data
    pd.testing.assert_frame_equal(actual_call_args["df"], expected_df)

    # Compare other arguments
    assert actual_call_args["database"] == "raw_glue_database"
    assert actual_call_args["table"] == SOURCE_TABLE_NAME
    assert (
        actual_call_args["table_location"]
        == "s3://a-bucket/table-location/float_rates/dirham_change_rates/"
    )
    assert (
        actual_call_args["temp_path"]
        == "s3://a-bucket/temp-path/float_rates/dirham_change_rates/"
    )


def test_athena_iceberg_exception(
    # set_hermes_config_folder,
    set_config_for_athena_iceberg,
    set_aws_env_vars,
    mock_athena_to_iceberg,
    mock_custom_source_extract,
    get_processed_float_rates_test_data,
):
    mock_athena_to_iceberg.side_effect = BotoCoreError
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline.run()
    ERRORS = [
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "demo_athena_iceberg",
            "error_type": "AthenaIcebergDestinationError",
            "error_message": "Athena Iceberg: error while loading data to raw_glue_database.dirham_change_rates.\n            table location: s3://a-bucket/table-location/float_rates/dirham_change_rates/, temp path: s3://a-bucket/temp-path/float_rates/dirham_change_rates/\n            error : An unspecified error occurred\n        ",
        }
    ]
    assert pipeline.errors == ERRORS
