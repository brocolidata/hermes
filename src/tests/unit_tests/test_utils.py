import pathlib
from unittest.mock import patch

import omegaconf

from hermes.utils import get_definitions_from_file


@patch("hermes.utils.settings.get_config_folder")
@patch("pathlib.Path.rglob")
@patch("hermes.utils.omegaconf.OmegaConf.load")
def test_load_definitions(mock_omegaconf_load, mock_rglob, mock_get_config_folder):
    """Test the load_definitions function."""

    # Mock the config folder path
    mock_get_config_folder.return_value = "/mock/config"

    # Mock found YAML files
    mock_file_1 = pathlib.Path("/mock/config/source1.yml")
    mock_rglob.return_value = [mock_file_1]
    TEST_CONFIG_SOURCEA = omegaconf.OmegaConf.create(
        {
            "sources": [
                {
                    "name": "sourceA",
                    "type": "custom",
                    "config": {
                        "extractor": "ExtractorSourceA",
                        "module_path": "moduleSourceA",
                        "tables": [
                            {
                                "name": "tableA",
                                "data_key": "table_a",
                                "kwargs": {"url": "https://www.sourceaurl.com"},
                            }
                        ],
                    },
                }
            ]
        }
    )
    # Mock YAML file contents
    mock_omegaconf_load.side_effect = [
        TEST_CONFIG_SOURCEA,
    ]

    # Run function
    definitions = get_definitions_from_file()

    # Assertions
    assert isinstance(definitions, omegaconf.dictconfig.DictConfig), (
        "Expected definitions to be a dictionary"
    )
    assert "sources" in definitions, "Expected 'sources' key in definitions"
    # assert definitions["sources"]["sourceA"] == "/mock/config/source1.yml"
    # assert definitions["sources"]["sourceB"] == "/mock/config/source2.yml"
    assert definitions.sources[0] == TEST_CONFIG_SOURCEA.sources[0]
