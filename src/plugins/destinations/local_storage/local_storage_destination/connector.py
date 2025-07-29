import omegaconf
from generic_object_storage_destination.connector import ObjectStorageDestination


class LocalStorageDestination(ObjectStorageDestination):
    def __init__(self, destination_config: omegaconf.dictconfig.DictConfig):
        """Create an instance of the connector

        Args:
            destination_config (omegaconf.dictconfig.DictConfig): configuration for the destination
        """
        super().__init__(destination_config)  # Call parent constructor
        self._prefix = ""

    @property
    def prefix(self):
        return self._prefix
