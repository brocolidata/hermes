import datetime as dt
from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError

import hermes

TEST_PIPELINE_NAME = "sync_float_rates"


@pytest.fixture
def set_config_for_custom_source(monkeypatch, test_folder):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv(
        "HERMES_ARTIFACTS_FOLDER",
        f"{test_folder}/assets/artifacts/custom",
    )
    yield


def test_custom_source(
    set_config_for_custom_source,
    set_aws_env_vars,
    mock_fsspec_open,
    mock_athena_to_iceberg,
    set_hermes_project_folder
):
    # hermes.run_pipeline(TEST_PIPELINE_NAME)
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline_run = pipeline.create_run()
    pipeline_run.run()

    # Assert successes are recorded in the Pipeline object
    SUCCESSES = [
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "landing_zone",
        },
        {
            "source_name": "float_rates",
            "source_table_name": "dirham_change_rates",
            "destination_name": "demo_athena_iceberg",
        },
    ]
    assert pipeline_run.successes == SUCCESSES


@patch("requests.get", side_effect=ConnectionError("Max retries exceeded with url"))
def test_custom_source_exception(
    mock_requests_get,
    set_config_for_custom_source,
    set_aws_env_vars,
    mock_fsspec_open,
    mock_athena_to_iceberg,
    set_hermes_project_folder,
    run_context_timestamps
):

    # hermes.run_pipeline(TEST_PIPELINE_NAME)
    pipeline = hermes.get_pipeline(TEST_PIPELINE_NAME)
    pipeline_run = pipeline.create_run(run_context=run_context_timestamps)
    pipeline_run.run()
    ERRORS = [
        {
            "source_name": "float_rates", 
            "source_table_name": "dirham_change_rates", 
            "destination_name": "landing_zone", "error_type": "CustomSourceError", 
            "error_message": "Custom Source: error during extracting for source float_rates.\n            error : Max retries exceeded with url", 
            "run_context": run_context_timestamps
        }, 
        {
            "source_name": "float_rates", 
            "source_table_name": "dirham_change_rates", 
            "destination_name": "demo_athena_iceberg", 
            "error_type": "CustomSourceError", 
            "error_message": "Custom Source: error during extracting for source float_rates.\n            error : Max retries exceeded with url", 
            "run_context": run_context_timestamps
        }
    ]
    assert pipeline_run.errors == ERRORS
