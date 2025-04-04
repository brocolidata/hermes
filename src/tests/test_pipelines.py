import os
import pathlib
from unittest.mock import mock_open, patch

import omegaconf
import pytest

import hermes


def get_test_pipelines():
    config_folder = os.getenv("HERMES_CONFIG_FOLDER")
    CONFIG_FILE = "test_pipelines.yml"
    config_file_path = pathlib.Path(config_folder, CONFIG_FILE)
    config = omegaconf.OmegaConf.load(config_file_path)
    pipeline_names = [p.name for p in config.pipelines]
    return pipeline_names


@pytest.fixture
def mock_fsspec_open():
    """Fixture to mock fsspec.open in a context manager."""
    mock_file = mock_open()
    with patch("fsspec.open", mock_file):
        yield mock_file  # Provide the mock to tests


@pytest.fixture
def set_aws_env_vars(monkeypatch):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-3")

    yield  # Provide the environment setup to tests


@pytest.fixture
def mock_athena_to_iceberg():
    """Fixture to mock awswrangler.athena.to_iceberg."""
    with patch("awswrangler.athena.to_iceberg") as mock_to_iceberg:
        yield mock_to_iceberg  # Provide the mock to tests


@pytest.mark.parametrize("pipeline_name", ["sync_float_rates"])
def test_multi_destination_pipelines(
    set_aws_env_vars,
    mock_fsspec_open,
    mock_athena_to_iceberg,
    pipeline_name,
):
    hermes.run_pipeline(pipeline_name)
