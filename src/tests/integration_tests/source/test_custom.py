import pytest

from hermes.pipeline import get_pipeline

TEST_PIPELINE_NAME = "sync_float_rates"


@pytest.fixture
def set_config_for_object_storage(monkeypatch, test_folder):
    """Fixture to set environment variables for tests."""
    monkeypatch.setenv(
        "HERMES_CONFIG_FOLDER",
        f"{test_folder}/assets/config/test_object_storage",
        # "HERMES_CONFIG_FOLDER", "tests/assets/config/test_object_storage"
    )
    yield  # Provide the environment setup to tests


def test_custom_source(
    set_hermes_config_folder,
    set_aws_env_vars,
    mock_fsspec_open,
    mock_athena_to_iceberg,
):
    # hermes.run_pipeline(TEST_PIPELINE_NAME)
    pipeline = get_pipeline(TEST_PIPELINE_NAME)
    print("hello")
