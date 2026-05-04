from importlib.metadata import entry_points

import omegaconf

from hermes.destinations.utils import BaseDestination
from hermes.exceptions import ConfigLoadError
from hermes.sources.utils import BaseSource


def get_connector(
    dc_connector: omegaconf.dictconfig.DictConfig, connector_meta_type_plural: str
) -> BaseSource | BaseDestination:
    """Load all installed plugins under a given entry point group."""
    connector_type = dc_connector.type
    entrypoints_group = f"hermes_plugins.{connector_meta_type_plural}"
    try:
        connector_entrypoint = entry_points(group=entrypoints_group)[connector_type]
        connector_class = connector_entrypoint.load()
        connector = connector_class(dc_connector)
        return connector
    except KeyError as e:
        raise ConfigLoadError(
            process_step="plugin retrieval", error=f"{str(e)} connector cannot be found"
        )
