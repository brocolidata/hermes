from unittest.mock import MagicMock, patch

import pytest
from omegaconf import DictConfig

from hermes.connectors import (
    get_connector,
    get_destination_connector,
    get_source_connector,
)
from hermes.destinations import athena_iceberg, object_storage
from hermes.sources import custom


@pytest.fixture
def mock_custom_source():
    """Fixture to create a mocked CustomSource instance."""
    return MagicMock(spec=custom.CustomSource)


@pytest.fixture
def mock_object_storage_destination():
    """Fixture to create a mocked ObjectStorageDestination instance."""
    return MagicMock(spec=object_storage.ObjectStorageDestination)


@pytest.fixture
def mock_athena_iceberg_destination():
    """Fixture to create a mocked AthenaIcebergDestination instance."""
    return MagicMock(spec=athena_iceberg.AthenaIcebergDestination)


@pytest.fixture
def source_config():
    """Fixture to create a source connector configuration."""
    return DictConfig({"type": "custom", "name": "test_source", "config": {}})


@pytest.fixture
def object_storage_config():
    """Fixture to create an object storage destination configuration."""
    return DictConfig(
        {"type": "object_storage", "name": "test_object_storage", "config": {}}
    )


@pytest.fixture
def athena_iceberg_config():
    """Fixture to create an Athena Iceberg destination configuration."""
    return DictConfig(
        {"type": "athena_iceberg", "name": "test_athena_iceberg", "config": {}}
    )


@patch("hermes.connectors.get_source_connector")
@patch("hermes.connectors.get_destination_connector")
def test_get_connector_source(
    mock_get_destination, mock_get_source, source_config, mock_custom_source
):
    """Test get_connector correctly calls get_source_connector for 'source' meta type."""
    mock_get_source.return_value = mock_custom_source

    connector = get_connector(source_config, "source")

    # Ensure get_source_connector was called and get_destination_connector was NOT
    mock_get_source.assert_called_once_with(source_config)
    mock_get_destination.assert_not_called()

    # Verify the returned object is the mocked CustomSource
    assert connector is mock_custom_source


@patch("hermes.sources.custom.CustomSource")
def test_get_custom_source_connector(
    mock_custom_source_class, source_config, mock_custom_source
):
    """Test that get_source_connector correctly returns a CustomSource instance."""
    mock_custom_source_class.return_value = mock_custom_source

    connector = get_source_connector(source_config)

    # Check if the correct class was instantiated
    mock_custom_source_class.assert_called_once_with(source_config)

    # Verify the returned object is the mocked CustomSource
    assert connector is mock_custom_source


@patch("hermes.connectors.get_source_connector")
@patch("hermes.connectors.get_destination_connector")
def test_get_connector_destination(
    mock_get_destination,
    mock_get_source,
    object_storage_config,
    mock_object_storage_destination,
):
    """Test get_connector correctly calls get_destination_connector for 'destination' meta type."""
    mock_get_destination.return_value = mock_object_storage_destination

    connector = get_connector(object_storage_config, "destination")

    # Ensure get_destination_connector was called and get_source_connector was NOT
    mock_get_destination.assert_called_once_with(object_storage_config)
    mock_get_source.assert_not_called()

    # Verify the returned object is the mocked ObjectStorageDestination
    assert connector is mock_object_storage_destination


@patch("hermes.destinations.object_storage.ObjectStorageDestination")
def test_get_destination_connector_object_storage(
    mock_object_storage_class, object_storage_config, mock_object_storage_destination
):
    """Test that get_destination_connector correctly returns an ObjectStorageDestination instance."""
    mock_object_storage_class.return_value = mock_object_storage_destination

    connector = get_destination_connector(object_storage_config)

    # Check if the correct class was instantiated
    mock_object_storage_class.assert_called_once_with(object_storage_config)

    # Verify the returned object is the mocked ObjectStorageDestination
    assert connector is mock_object_storage_destination


@patch("hermes.destinations.athena_iceberg.AthenaIcebergDestination")
def test_get_destination_connector_athena_iceberg(
    mock_athena_iceberg_class, athena_iceberg_config, mock_athena_iceberg_destination
):
    """Test that get_destination_connector correctly returns an AthenaIcebergDestination instance."""
    mock_athena_iceberg_class.return_value = mock_athena_iceberg_destination

    connector = get_destination_connector(athena_iceberg_config)

    # Check if the correct class was instantiated
    mock_athena_iceberg_class.assert_called_once_with(athena_iceberg_config)

    # Verify the returned object is the mocked AthenaIcebergDestination
    assert connector is mock_athena_iceberg_destination
