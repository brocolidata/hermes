import pandas as pd
import pytest

import hermes

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
    hermes.run_pipeline(TEST_PIPELINE_NAME)
    # Ensure function was called once
    mock_athena_to_iceberg.assert_called_once()

    # Extract the actual call arguments
    actual_call_args = mock_athena_to_iceberg.call_args.kwargs

    # Compare DataFrame separately
    expected_df = get_processed_float_rates_test_data
    pd.testing.assert_frame_equal(actual_call_args["df"], expected_df)

    # Compare other arguments
    assert actual_call_args["database"] == f"dl_raw_{SOURCE_NAME}"
    assert actual_call_args["table"] == SOURCE_TABLE_NAME
    assert actual_call_args["table_location"] == "a-bucket"
    assert actual_call_args["temp_path"] == ""
