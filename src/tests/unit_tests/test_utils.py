import pathlib
from unittest.mock import MagicMock, mock_open, patch

import omegaconf
import pytest

from hermes.utils import (
    get_definitions_from_file,
    load_and_merge_configs,
    load_definitions,
    write_definitions,
)


# Mock settings module
@pytest.fixture
def mock_settings():
    with patch("hermes.utils.settings") as mock_settings:
        yield mock_settings


@pytest.fixture
def mock_config_path():
    """Mock the configuration folder path."""
    with patch(
        "hermes.settings.get_config_folder", return_value=pathlib.Path("/mock/config")
    ):
        yield


@pytest.fixture
def mock_definition_file():
    """Mock the definition file path."""
    with patch(
        "hermes.settings.get_definition_file_path",
        return_value=pathlib.Path("/mock/definitions.yml"),
    ):
        yield


@pytest.fixture
def mock_node_types():
    """Mock the NodeTypes enum values."""
    with patch(
        "hermes.settings.NodeTypes",
        MagicMock(
            SOURCES="sources", DESTINATIONS="destinations", PIPELINES="pipelines"
        ),
    ):
        yield


@patch("hermes.utils.settings.get_config_folder")
@patch("pathlib.Path.rglob")
@patch("hermes.utils.omegaconf.OmegaConf.load")
def test_load_definitions(mock_omegaconf_load, mock_rglob, mock_get_config_folder):
    """Test the load_definitions function."""

    # Mock the config folder path
    mock_get_config_folder.return_value = "/mock/config"

    # Mock found YAML files
    mock_file_1 = pathlib.Path("/mock/config/source1.yml")
    mock_file_2 = pathlib.Path("/mock/config/source2.yml")
    mock_rglob.return_value = [mock_file_1, mock_file_2]

    # Mock YAML file contents
    mock_omegaconf_load.side_effect = [
        omegaconf.OmegaConf.create({"sources": [{"name": "sourceA"}]}),  # source1.yml
        omegaconf.OmegaConf.create({"sources": [{"name": "sourceB"}]}),  # source2.yml
    ]

    # Run function
    definitions = load_definitions()

    # Assertions
    assert isinstance(definitions, dict), "Expected definitions to be a dictionary"
    assert "sources" in definitions, "Expected 'sources' key in definitions"
    assert definitions["sources"]["sourceA"] == "/mock/config/source1.yml"
    assert definitions["sources"]["sourceB"] == "/mock/config/source2.yml"

    # Ensure files were loaded
    mock_omegaconf_load.assert_any_call(mock_file_1)
    mock_omegaconf_load.assert_any_call(mock_file_2)


@pytest.fixture
def mock_load_definitions():
    with patch("hermes.utils.load_definitions") as mock_load_definitions:
        yield mock_load_definitions


def test_write_definitions(mock_settings, mock_load_definitions):
    # Prepare mock return values
    mock_load_definitions.return_value = {
        "sources": {"source1": "/mock/path/source.yml"}
    }
    mock_settings.get_definition_file_path.return_value = "/mock/path/definitions.yml"

    # Mock the file system methods
    mock_artifact_file_path = MagicMock()
    mock_artifact_file_path.exists.return_value = False  # Simulate file doesn't exist
    mock_artifact_file_path.parent.exists.return_value = (
        False  # Simulate parent directory doesn't exist
    )

    # Set the mock to return this artifact path
    mock_settings.get_definition_file_path.return_value = mock_artifact_file_path

    # Patch open and json.dump to avoid actual file operations
    with (
        patch("builtins.open", mock_open()) as mocked_file,
        patch("json.dump") as mock_json_dump,
    ):
        # Run the function under test
        write_definitions()

        # Check if the parent directory is created (mkdir should be called)
        mock_artifact_file_path.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )

        # Check if the file is opened with the correct path and write mode
        mocked_file.assert_called_once_with(mock_artifact_file_path, "w")

        # Ensure json.dump is called with the correct data (mocked definitions)
        mock_json_dump.assert_called_once_with(
            {"sources": {"source1": "/mock/path/source.yml"}}, mocked_file()
        )

        # Check that exists method was called on artifact_file_path
        mock_artifact_file_path.exists.assert_called_once()


@patch("hermes.utils.omegaconf.OmegaConf.load")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"sources": {"source1": "/mock/path.yml"}}',
)
def test_get_definitions_from_file(
    mock_open_file, mock_omegaconf_load, mock_definition_file
):
    """Test getting definitions from a file."""
    mock_omegaconf_load.return_value = omegaconf.OmegaConf.create(
        {"sources": {"source1": "/mock/path.yml"}}
    )

    definitions = get_definitions_from_file()

    assert "sources" in definitions
    assert definitions["sources"]["source1"] == "/mock/path.yml"
    mock_omegaconf_load.assert_called_once_with(pathlib.Path("/mock/definitions.yml"))


@patch("hermes.utils.omegaconf.OmegaConf.load")
def test_load_and_merge_configs(mock_omegaconf_load, mock_settings):
    # Mock the config folder path
    mock_settings.get_config_folder.return_value = pathlib.Path("/mock/config/folder")

    # Mock the loaded config file data
    mock_omegaconf_load.side_effect = [
        omegaconf.OmegaConf.create({"sources": [{"name": "source1"}]}),
        omegaconf.OmegaConf.create({"destinations": [{"name": "destination1"}]}),
    ]

    # Mock the filesystem rglob to return some mock config files
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.return_value = [
            pathlib.Path("/mock/config/file1.yml"),
            pathlib.Path("/mock/config/file2.yml"),
        ]

        # Mock the file system methods
        mock_artifact_file_path = MagicMock()
        mock_artifact_file_path.exists.return_value = (
            False  # Simulate file doesn't exist
        )
        mock_artifact_file_path.parent.exists.return_value = (
            False  # Simulate parent directory doesn't exist
        )

        # Set the mock to return this artifact path
        mock_settings.get_definition_file_path.return_value = mock_artifact_file_path

        # Patch open and json.dump to avoid actual file operations
        with (
            patch("builtins.open", mock_open()) as mock_open_file,
            patch("json.dump") as mock_json_dump,
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.mkdir"),
        ):
            load_and_merge_configs()

            # Check if the file was opened with the correct path and write mode
            mock_open_file.assert_called_once_with(mock_artifact_file_path, "w")

            # Retrieve the handle to check write calls
            handle = mock_open_file()

            # Ensure json.dump was called with the correct merged data
            mock_json_dump.assert_called_once_with(
                {
                    "sources": [{"name": "source1"}],
                    "destinations": [{"name": "destination1"}],
                    "pipelines": [],
                },
                handle,
                indent=2,
            )
