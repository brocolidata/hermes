import awswrangler as wr
import omegaconf

from hermes.destinations.utils import BaseDestination


class AthenaIcebergDestination(BaseDestination):
    """Destination connector for Apache Iceberg tables in AWS Athena."""

    def __init__(self, destination_config: omegaconf.dictconfig.DictConfig):
        """Create an instance of the connector

        Args:
            destination_config (omegaconf.dictconfig.DictConfig): configuration for the destination
        """
        self.config = destination_config.config
        # self.bucket = self.config.bucket
        # self.file_format = self.config.format
        # self.service = self.config.service
        # self.prefix = self._get_prefix()
        # self.format = self.config.format
        self.data_stage = "processed"

        self.glue_database = self.config.glue_database
        # self.glue_table = self.config.glue_table
        self.table_location = self.config.table_location

    def get_temp_path(self):
        return ""

    # def load(self, dc_extract_outputs:dict[str, pd.DataFrame]):
    def load(self, source_name, source_table_name, data):
        """Load data outputs of extract connector to destination

        Args:
            dc_extract_outputs (dict[str, pd.DataFrame]): Outputs of extract connector
        """
        # source_name = list(dc_extract_outputs.keys())[0]
        # for table_name, df in dc_extract_outputs[source_name].items():
        # TODO: Determine how source is used (dedicated Glue database or use it as prefix in table name)
        wr.athena.to_iceberg(
            df=data,
            # database=self.glue_database,
            database=f"dl_raw_{source_name}",
            # table=self.glue_table,
            table=source_table_name,
            table_location=self.table_location,
            temp_path=self.get_temp_path(),
        )
