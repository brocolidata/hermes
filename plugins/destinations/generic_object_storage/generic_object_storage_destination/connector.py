import abc
import datetime
import json

import fsspec
import omegaconf

from generic_object_storage_destination.exceptions import ObjectStorageDestinationError
from hermes.destinations.utils import BaseDestination


class ObjectStorageDestination(BaseDestination):
    """Destination connector for Object Storage services.

    Included services :
    - Google Cloud Storage
    - AWS S3
    """

    def __init__(self, destination_config: omegaconf.dictconfig.DictConfig):
        """Create an instance of the connector

        Args:
            destination_config (omegaconf.dictconfig.DictConfig): configuration for the destination
        """
        self.config = destination_config.config
        self.name = destination_config.name
        self.bucket = self.config.bucket
        self.format = self.config.format
        self.data_stage = "raw"

    @property
    @abc.abstractmethod
    def prefix(self):
        pass

    def get_object_path(self, source_name, source_table_name: str) -> str:
        """Get full object path

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table

        Returns:
            str: Full object path
        """
        timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        path = f"{self.prefix}/{self.bucket}/{source_name}/{source_table_name}/{source_table_name}_{timestamp}.{self.format}"
        return path

    def load(self, source_name: str, source_table_name: str, data):
        """Load data outputs of extract connector to destination

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table
            data (_type_): data to load

        Raises:
            ObjectStorageDestinationError: if any exception is raised during load to destination
        """
        file_path = self.get_object_path(source_name, source_table_name)
        try:
            fs = fsspec.open(urlpath=file_path, mode="w")
            with fs as f:
                json.dump(data, f)
        except Exception as e:
            raise ObjectStorageDestinationError(
                name=self.name, path=file_path, error=str(e)
            )
