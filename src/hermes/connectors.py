import omegaconf

from hermes.destinations import object_storage
from hermes.destinations.utils import BaseDestination
from hermes.sources import custom
from hermes.sources.utils import BaseSource


def get_source_connector(source_config:omegaconf.dictconfig.DictConfig) -> BaseSource:
    """Get the source connector corresponding to the source config type

    Args:
        source_config (omegaconf.dictconfig.DictConfig): Source configuration

    Returns:
        BaseSource: Source connector object
    """
    match source_config.type:
        case 'custom':
            connector = custom.CustomSource(source_config)
    return connector
        

def get_destination_connector(destination_config:omegaconf.dictconfig.DictConfig) -> BaseDestination:
    """Get the destination connector corresponding to the destination config type

    Args:
        destination_config (omegaconf.dictconfig.DictConfig): Destination configuration

    Returns:
        BaseDestination: Destination connector object

    """
    match destination_config.type:
        case 'object_storage':
            connector = object_storage.ObjectStorageDestination(destination_config)
    return connector

        

