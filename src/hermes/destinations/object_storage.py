import omegaconf
import pandas as pd

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

    def _get_prefix(self) -> str:
        """Get prefix for object storage URI

        Returns:
            str: Prefix
        """
        prefix = getattr(
            settings.ObjectStorageServicesPrefixes, 
            self.service
        ).value
        return prefix
    
    def get_object_path(self, table: str) -> str:
        """Get object storage URI

        Args:
            table (str): Destination table name

        Returns:
            str: _description_
        """
        path = f"{self.prefix}://{self.bucket}/{table}/{table}.{self.format}"
        return path

    def load(self, dc_extract_outputs:dict[str, pd.DataFrame]):
        """Load data outputs of extract connector to destination

        Args:
            dc_extract_outputs (dict[str, pd.DataFrame]): Outputs of extract connector
        """
        for table, df in dc_extract_outputs.items():
            object_path = self.get_object_path(table)
            df.to_parquet(object_path)