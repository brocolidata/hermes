import pathlib
from unittest.mock import mock_open, patch

import omegaconf
import pytest

from hermes.exceptions import ConfigLoadError
from plugins.utils.hermes_cli.cli.main import (load_and_merge_configs,
                                               parse_project,
                                               validate_definition_file,
                                               write_definitions)


@pytest.fixture
def valid_definitions():
    return {
        "sources": [
            {
                "name": "source1",
                "type": "custom",
                "config": {"extractor": "e", "module_path": "m", "tables": []},
            }
        ],
        "destinations": [
            {
                "name": "dest1",
                "type": "object_storage",
                "config": {"service": "s3", "format": "parquet", "bucket": "my-bucket"},
            }
        ],
        "pipelines": [],
    }


@pytest.fixture
def invalid_definitions():
    return {
        "sources": [{"name": "source1", "type": "custom"}],  # missing config
        "destinations": [],
        "pipelines": [],
    }


@patch("pathlib.Path.rglob")
@patch("omegaconf.OmegaConf.load")
@patch("hermes.settings")
def test_load_and_merge_configs(mock_settings, mock_omegaconf_load, mock_rglob, set_hermes_project_folder):
    mock_settings.get_config_folder.return_value = pathlib.Path("/mock/config")
    mock_rglob.return_value = [pathlib.Path("a.yml"), pathlib.Path("b.yml")]

    mock_omegaconf_load.side_effect = [
        omegaconf.OmegaConf.create({"sources": [{"name": "s1"}]}),
        omegaconf.OmegaConf.create({"destinations": [{"name": "d1"}]}),
    ]

    definitions = load_and_merge_configs(None)

    assert definitions["sources"] == [{"name": "s1"}]
    assert definitions["destinations"] == [{"name": "d1"}]
    assert definitions["pipelines"] == []


def test_write_definitions_creates_file(tmp_path):
    definitions = {"sources": [], "destinations": [], "pipelines": []}
    fake_path = tmp_path / "output"

    with (
        patch("builtins.open", mock_open()) as mock_file,
        patch("json.dump") as mock_json_dump,
    ):
        write_definitions(definitions, fake_path)

    mock_file.assert_called_once_with(fake_path / "definitions.json", "w")
    mock_json_dump.assert_called_once_with(definitions, mock_file(), indent=2)


@patch("plugins.utils.hermes_cli.cli.main.get_json_schema")
def test_validate_definition_file_valid(mock_get_schema, valid_definitions):
    mock_get_schema.return_value = {
        "type": "object",
        "properties": {
            "sources": {"type": "array"},
            "destinations": {"type": "array"},
            "pipelines": {"type": "array"},
        },
        "required": ["sources", "destinations", "pipelines"],
    }
    try:
        validate_definition_file(valid_definitions)
    except ConfigLoadError:
        pytest.fail("Unexpected ConfigLoadError raised")


@patch("plugins.utils.hermes_cli.cli.main.get_json_schema")
def test_validate_definition_file_invalid(mock_get_schema, invalid_definitions):
    mock_get_schema.return_value = {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {"type": "object", "required": ["config"]},
            },
            "destinations": {"type": "array"},
            "pipelines": {"type": "array"},
        },
        "required": ["sources", "destinations", "pipelines"],
    }

    with pytest.raises(ConfigLoadError):
        validate_definition_file(invalid_definitions)

@patch("plugins.utils.hermes_cli.cli.main.write_definitions")
@patch("plugins.utils.hermes_cli.cli.main.validate_definition_file")
@patch("plugins.utils.hermes_cli.cli.main.load_and_merge_configs")
@patch("hermes.settings")
def test_parse_project_success(mock_settings, mock_load, mock_validate, mock_write, set_hermes_project_folder):
    mock_load.return_value = {"sources": [], "destinations": [], "pipelines": []}
    mock_settings.get_config_folder.return_value = pathlib.Path("/mock/config")
    mock_settings.get_artifacts_folder.return_value = pathlib.Path("/mock/artifacts")
    mock_settings.get_custom_connectors_folder.return_value = pathlib.Path(
        "/mock/custom"
    )

    result = parse_project()
    assert result is True
