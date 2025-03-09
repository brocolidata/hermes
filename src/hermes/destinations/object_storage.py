import json

import fsspec
import omegaconf

from hermes import settings
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
        self.bucket = self.config.bucket
        self.file_format = self.config.format
        self.service = self.config.service
        self.prefix = self._get_prefix()
        self.format = self.config.format
        self.data_stage = "raw"

    def _get_prefix(self) -> str:
        """Get prefix for object storage URI

        Returns:
            str: Prefix
        """
        prefix = getattr(settings.ObjectStorageServicesPrefixes, self.service).value
        return prefix

    def get_object_path(self, source_name, source_table_name: str) -> str:
        """Get object storage URI

        Args:
            source_name (str): Name of the source
            source_table_name (str): Name of the source table

        Returns:
            str: The destination path of the file in the object storage service
        """
        # TODO: Define a convention for the landing zone path (include an ID, timestamp)
        path = f"{self.prefix}://{self.bucket}/{source_name}/{source_table_name}.{self.format}"
        return path

    def load(self, source_name, source_table_name, data):
        file_path = self.get_object_path(source_name, source_table_name)
        fs = fsspec.open(urlpath=file_path, mode="w")
        with fs as f:
            json.dump(data, f)
