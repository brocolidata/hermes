import awswrangler as wr
import omegaconf
import pandas as pd

from athena_iceberg_destination.exceptions import (
    AthenaIcebergDestinationError,
)
from hermes.destinations.utils import BaseDestination
from hermes.logging_utils import get_logger
from hermes.settings import ATHENA_ICEBERG_ANTE_PROCESS_MSG

logger = get_logger()


class AthenaIcebergDestination(BaseDestination):
    """Destination connector for Apache Iceberg tables in AWS Athena."""

    def __init__(self, destination_config: omegaconf.dictconfig.DictConfig):
        """Create an instance of the connector

        Args:
            destination_config (omegaconf.dictconfig.DictConfig): configuration for the destination
        """
        self.config = destination_config.config
        self.name = destination_config.name
        self.data_stage = "processed"
        self.temp_path = self.config.temp_path
        self.glue_database = self.config.glue_database
        self.table_location = self.config.table_location
        self.workgroup = self.config.get("workgroup", "primary")

    def _get_full_table_location(self, source_name: str, source_table_name: str) -> str:
        """Return full table path

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table

        Returns:
            str: full table path
        """
        table_location = f"{self.table_location}/{source_name}/{source_table_name}/"
        return table_location

    def _get_full_temp_path(self, source_name: str, source_table_name: str) -> str:
        """Return full temp path

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table

        Returns:
            str: full temp path
        """
        temp_path = f"{self.temp_path}/{source_name}/{source_table_name}/"
        return temp_path

    def load(self, source_name: str, source_table_name: str, data: pd.DataFrame):
        """Load data outputs of extract connector to destination

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table
            data (pd.DataFrame): data to load

        Raises:
            AthenaIcebergDestinationError: if any exception is raised during load to destination
        """
        # TODO: Determine how source is used (dedicated Glue database or use it as prefix in table name)
        table_location = self._get_full_table_location(source_name, source_table_name)
        temp_path = self._get_full_temp_path(source_name, source_table_name)
        # Logging Ante
        formated_ante_msg = ATHENA_ICEBERG_ANTE_PROCESS_MSG.format(
            glue_database=self.glue_database,
            glue_table=source_table_name,
            table_location=table_location,
            temp_path=temp_path,
        )
        logger.info(formated_ante_msg)
        try:
            wr.athena.to_iceberg(
                df=data,
                database=self.glue_database,
                table=source_table_name,
                table_location=table_location,
                temp_path=temp_path,
                workgroup=self.workgroup,
            )
        except Exception as e:
            raise AthenaIcebergDestinationError(
                glue_database=self.glue_database,
                glue_table=source_table_name,
                table_location=table_location,
                temp_path=temp_path,
                process_step="load to",
                error=str(e),
            )
