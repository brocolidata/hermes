import awswrangler as wr
import omegaconf

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

    def _get_table_location(self, source_name: str, source_table_name: str) -> str:
        table_location = f"{self.table_location}/{source_name}/{source_table_name}/"
        return table_location

    def _get_temp_path(self, source_name: str, source_table_name: str) -> str:
        temp_path = f"{self.temp_path}/{source_name}/{source_table_name}/"
        return temp_path

    def load(self, source_name, source_table_name, data):
        """Load data outputs of extract connector to destination

        Args:
            dc_extract_outputs (dict[str, pd.DataFrame]): Outputs of extract connector
        """
        # TODO: Determine how source is used (dedicated Glue database or use it as prefix in table name)
        table_location = self._get_table_location(source_name, source_table_name)
        temp_path = self._get_temp_path(source_name, source_table_name)
        # Logging Ante
        formated_ante_msg = ATHENA_ICEBERG_ANTE_PROCESS_MSG.format(
            glue_database=self.glue_database,
            glue_table=source_table_name,
            table_location=table_location,
            temp_path=temp_path,
        )
        logger.info(formated_ante_msg)
        wr.athena.to_iceberg(
            df=data,
            database=self.glue_database,
            table=source_table_name,
            table_location=table_location,
            temp_path=temp_path,
        )
