# TODO: add tests for hermes.connectors

from unittest.mock import MagicMock, patch

import omegaconf
import pytest

from hermes.connectors import get_connector
from hermes.exceptions import ConfigLoadError


def test_get_connector_success():
    """Test successful connector loading."""
    mock_entry_point = MagicMock()
    mock_class = MagicMock()
    mock_connector = MagicMock()
    mock_class.return_value = mock_connector
    mock_entry_point.load.return_value = mock_class

    mock_entry_points = {
        "test_source": mock_entry_point,
    }

    mock_dc_connector = omegaconf.OmegaConf.create(
        {"type": "test_source", "some_config": "value"}
    )

    with patch("hermes.connectors.entry_points", return_value=mock_entry_points):
        result = get_connector(mock_dc_connector, "sources")
        assert result == mock_connector
        mock_entry_point.load.assert_called_once()
        mock_class.assert_called_once_with(mock_dc_connector)


def test_get_connector_key_error():
    """Test connector loading with a non-existent connector type."""
    mock_entry_points = {}  # Empty entry points to simulate missing connector

    mock_dc_connector = omegaconf.OmegaConf.create(
        {"type": "nonexistent_source", "some_config": "value"}
    )

    with patch("hermes.connectors.entry_points", return_value=mock_entry_points):
        with pytest.raises(ConfigLoadError):
            get_connector(mock_dc_connector, "sources")


def test_get_connector_correct_entrypoint_group():
    """Test connector loading with correct entry point group construction."""
    mock_entry_point = MagicMock()
    mock_class = MagicMock()
    mock_connector = MagicMock()
    mock_class.return_value = mock_connector
    mock_entry_point.load.return_value = mock_class

    mock_entry_points = {
        "test_destination": mock_entry_point,
    }

    mock_dc_connector = omegaconf.OmegaConf.create(
        {"type": "test_destination", "some_config": "value"}
    )

    with patch(
        "hermes.connectors.entry_points", return_value=mock_entry_points
    ) as mock_entry_points_fn:
        result = get_connector(mock_dc_connector, "destinations")
        assert result == mock_connector
        mock_entry_points_fn.assert_called_once_with(
            group="hermes_plugins.destinations"
        )
