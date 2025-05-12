# test_destination_variables.py

from unittest.mock import MagicMock, Mock, patch

import omegaconf
import pytest

from hermes.destinations.variables import (
    fetch_destination_and_variable_config,
    fetch_destination_variable,
    parse_destination_string,
    process_destination_variable_kwargs,
)
from hermes.exceptions import ConfigLoadError


def test_parse_destination_string_valid():
    var = "$destinations.athena.variables.max_date"
    destination, variable = parse_destination_string(var)
    assert destination == "athena"
    assert (
        variable == "athena"
    )  # <- NOTE: You probably meant variable_name here, not destination_name again.


def test_parse_destination_string_invalid():
    with pytest.raises(ConfigLoadError):
        parse_destination_string("$invalid_format")


def test_fetch_destination_and_variable_config_success():
    mock_definitions = Mock()
    mock_destination = Mock()
    mock_destination.name = "athena"
    mock_destination.variables = {"max_date": {"column": "date"}}
    mock_definitions.destinations = [mock_destination]

    with (
        patch(
            "hermes.utils.get_definitions_from_file",
            return_value=mock_definitions,
        ),
        patch(
            "hermes.destinations.variables.parse_destination_string",
            return_value=("athena", "max_date"),
        ),
    ):
        config, var_name, var_cfg = fetch_destination_and_variable_config(
            "$destinations.athena.variables.max_date"
        )

    assert config == mock_destination
    assert var_name == "max_date"
    assert var_cfg == {"column": "date"}


def test_fetch_destination_and_variable_config_failure():
    with (
        patch(
            "hermes.utils.get_definitions_from_file",
            side_effect=Exception("boom"),
        ),
        patch(
            "hermes.destinations.variables.parse_destination_string",
            return_value=("athena", "max_date"),
        ),
    ):
        with pytest.raises(ConfigLoadError) as exc_info:
            fetch_destination_and_variable_config(
                "$destinations.athena.variables.max_date"
            )
        assert (
            "loading $destinations.athena.variables.max_date destination variable"
            in str(exc_info.value)
        )


def test_fetch_destination_variable():
    """Test fetching a destination variable."""
    mock_get_connector = MagicMock()
    mock_destination_connector = MagicMock()
    mock_get_connector.return_value = mock_destination_connector
    mock_destination_connector.get_destination_variable.return_value = {
        "extracted": "data"
    }

    mock_destination_config = MagicMock()
    mock_variable_config = MagicMock()
    mock_fetch_destination_and_variable_config = MagicMock(
        return_value=(mock_destination_config, "test_var", mock_variable_config)
    )

    with (
        patch(
            "hermes.connectors.get_connector",
            mock_get_connector,
        ),
        patch(
            "hermes.destinations.variables.fetch_destination_and_variable_config",
            mock_fetch_destination_and_variable_config,
        ),
    ):
        result = fetch_destination_variable(
            "$destinations.test_dest.variables.test_var", "test_table"
        )

    assert result == {"extracted": "data"}
    mock_get_connector.assert_called_once_with(mock_destination_config, "destinations")
    mock_destination_connector.get_destination_variable.assert_called_once_with(
        "test_var", mock_variable_config, "test_table"
    )


## TODO: Create a test for process_destination_variable_kwargs
def test_process_destination_variable_kwargs():
    """Test processing of destination variable kwargs."""
    mock_fetch_destination_variable = MagicMock(return_value={"test": "value"})
    ls_destination_variables = ["var1", "var2", "var3"]
    pipeline_cache = {"var2": "cached_value"}

    with patch(
        "hermes.destinations.variables.fetch_destination_variable",
        mock_fetch_destination_variable,
    ):
        result = process_destination_variable_kwargs(
            ls_destination_variables, "test_table", pipeline_cache
        )

    expected_result = omegaconf.OmegaConf.create(
        {"var1": {"test": "value"}, "var3": {"test": "value"}}
    )

    assert result == expected_result
    mock_fetch_destination_variable.assert_called()
    assert mock_fetch_destination_variable.call_count == 2
