import json
import pathlib
from unittest.mock import mock_open, patch

import omegaconf
import pandas as pd
import pytest

import hermes
import hermes.sources


@pytest.fixture
def set_aws_env_vars(monkeypatch):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-3")

    yield  # Provide the environment setup to tests


@pytest.fixture
def set_hermes_config_folder(monkeypatch):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv(
        "HERMES_CONFIG_FOLDER", "tests/assets/config/test_athena_iceberg"
    )
    yield  # Provide the environment setup to tests


@pytest.fixture
def mock_fsspec_open():
    """Fixture to mock fsspec.open in a context manager."""
    mock_file = mock_open()

    # Ensure `.__enter__()` returns a file-like object
    mock_open_instance = mock_file.return_value.__enter__.return_value

    with patch("fsspec.open", mock_file) as mocked_open:
        yield mocked_open, mock_open_instance  # Provide both mock objects


@pytest.fixture
def mock_athena_to_iceberg():
    """Fixture to mock awswrangler.athena.to_iceberg."""
    with patch("awswrangler.athena.to_iceberg") as mock_to_iceberg:
        yield mock_to_iceberg  # Provide the mock to tests


## CUSTOM SOURCE FIXTURES

DIRHAM_CHANGE_RATES_TEST_DATA = pathlib.Path(
    pathlib.Path(__file__).resolve().parent,
    "assets",
    "data",
    "dirham_change_rates.json",
)


@pytest.fixture
def get_dirham_change_rates_data():
    with open(DIRHAM_CHANGE_RATES_TEST_DATA, "r") as f:
        json_data = json.load(f)
    return json_data


@pytest.fixture
def mock_custom_source_extract(get_dirham_change_rates_data):
    """Fixture to patch CustomSource.extract and return JSON content as DataFrame."""

    with patch.object(
        hermes.sources.custom.CustomSource,
        "extract",
        return_value={"float_rates": get_dirham_change_rates_data},
    ) as mock_extract:
        yield mock_extract  # Provide the mock to tests


@pytest.fixture
def get_processed_float_rates_test_data(get_dirham_change_rates_data):
    df = pd.DataFrame(list(get_dirham_change_rates_data.values()))
    return df


@pytest.fixture
def demo_config():
    TEST_CONFIG_PATH = pathlib.Path(
        pathlib.Path(__file__).resolve().parent,
        "assets",
        "config",
        "test_pipelines.yml",
    )
    config = omegaconf.OmegaConf.load(TEST_CONFIG_PATH)
    return config
