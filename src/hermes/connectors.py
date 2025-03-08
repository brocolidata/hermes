import omegaconf

from hermes.destinations import object_storage, athena_iceberg
from hermes.destinations.utils import BaseDestination
from hermes.sources import custom
from hermes.sources.utils import BaseSource


def get_connector(
    dc_connector: omegaconf.dictconfig.DictConfig, connector_meta_type: str
) -> BaseSource | BaseDestination:
    """_summary_

    Args:
        dc_connector (omegaconf.dictconfig.DictConfig): Connector configuration
        connector_meta_type (str): Meta type of the connector

    Returns:
        BaseSource | BaseDestination: Corresponding connector
    """
    match connector_meta_type:
        case "source":
            return get_source_connector(dc_connector)
        case "destination":
            return get_destination_connector(dc_connector)


def get_source_connector(dc_connector: omegaconf.dictconfig.DictConfig) -> BaseSource:
    """Get the source connector corresponding to the source config type

    Args:
        source_config (omegaconf.dictconfig.DictConfig): Source configuration

    Returns:
        BaseSource: Source connector object
    """
    match dc_connector.type:
        case "custom":
            connector = custom.CustomSource(dc_connector)
    return connector


def get_destination_connector(
    dc_connector: omegaconf.dictconfig.DictConfig,
) -> BaseDestination:
    """Get the destination connector corresponding to the destination config type

    Args:
        destination_config (omegaconf.dictconfig.DictConfig): Destination configuration

    Returns:
        BaseDestination: Destination connector object

    """
    match dc_connector.type:
        case "object_storage":
            connector = object_storage.ObjectStorageDestination(dc_connector)
        case "athena_iceberg":
            connector = athena_iceberg.AthenaIcebergDestination(dc_connector)
    return connector
