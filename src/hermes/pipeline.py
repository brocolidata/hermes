import omegaconf
from hermes import connectors, utils, logging_utils

logger = logging_utils.get_logger()


class Pipeline:
    """Represents a data pipeline, managing sources, destinations, and data processing."""

    def __init__(self, pipeline: omegaconf.dictconfig.DictConfig):
        """Initialize a pipeline with configuration details.

        Args:
            pipeline (omegaconf.dictconfig.DictConfig): Configuration for the pipeline.
        """
        self.pipeline_config = pipeline
        self.pipeline_name = pipeline.name
        self.schedule = pipeline.schedule
        self.sources_tables = self._get_sources_tables()
        self.destinations_names = pipeline.destinations
        self.sources_connectors = self._get_sources_connectors()
        self.destinations_connectors = self._get_destinations_connectors()

    def _get_sources_tables(self) -> dict[str, list]:
        """Retrieve source tables from the pipeline configuration.

        Returns:
            dict[str, list]: Mapping of source names to lists of table names.
        """
        dc_sources_tables_map = {}
        for dc_pipeline_source in self.pipeline_config.sources:
            source_name = dc_pipeline_source.name
            dc_sources_tables_map[source_name] = dc_pipeline_source.tables
        return dc_sources_tables_map

    def _get_connector_names_by_metatype(self, connector_meta_type: str) -> list[str]:
        """Retrieve connector names based on their type (source or destination).

        Args:
            connector_meta_type (str): Type of connector ('source' or 'destination').

        Returns:
            list[str]: List of connector names of the specified type.
        """
        match connector_meta_type:
            case "source":
                names = list(self.sources_tables.keys())
            case "destination":
                names = self.destinations_names
        return names

    def _get_tables_for_source(self, source_name: str) -> list[str]:
        """Retrieve the list of tables for a given source.

        Args:
            source_name (str): Name of the source.

        Returns:
            list[str]: List of table names for the specified source.
        """
        return self.sources_tables[source_name]

    def _get_connector(self, connector_meta_type: str) -> list:
        """Retrieve connector objects based on the connector type.

        Args:
            connector_meta_type (str): Type of connector ('source' or 'destination').

        Returns:
            list: List of connector objects.
        """
        definitions = utils.get_definitions_from_file()
        meta_type_plural = f"{connector_meta_type}s"
        connectors_configs = list(
            filter(
                lambda c: c.name
                in self._get_connector_names_by_metatype(connector_meta_type),
                definitions[meta_type_plural],
            )
        )
        connectors_objs = [
            connectors.get_connector(dc_connector, connector_meta_type)
            for dc_connector in connectors_configs
        ]
        return connectors_objs

    def _get_sources_connectors(self) -> list:
        """Retrieve source connectors.

        Returns:
            list: List of source connector objects.
        """
        return self._get_connector("source")

    def _get_destinations_connectors(self) -> list:
        """Retrieve destination connectors.

        Returns:
            list: List of destination connector objects.
        """
        return self._get_connector("destination")

    def _process_extract(
        self, source_extract, source_connector, source_table_name, data_stage
    ):
        """Process extracted data based on the data stage (raw or processed).

        Args:
            source_extract: Extracted data.
            source_connector: Connector object for the source.
            source_table_name (str): Name of the source table.
            data_stage (str): Stage of data processing ('raw' or 'processed').

        Returns:
            Processed data.
        """
        table_config = source_connector._get_table_config(source_table_name)
        data_key = table_config.get(
            "data_key", "data"
        )  # TODO: Make sure we want to do that here and this way
        match data_stage:
            case "raw":
                output = source_extract[data_key]
            case "processed":
                logger.info(f"Processing {source_connector.name} raw data..")
                output = source_connector.process_data(source_extract)
                logger.info(f"Successfully processed {source_connector.name} raw data")
        return output

    def _process_extract_and_load(
        self, source_extract, source_table_name, source_connector, destination_connector
    ):
        """Process and load extracted data to the destination connector.

        Args:
            source_extract: Extracted data.
            source_table_name (str): Name of the source table.
            source_connector: Source connector object.
            destination_connector: Destination connector object.
        """
        data = self._process_extract(
            source_extract=source_extract,
            source_connector=source_connector,
            source_table_name=source_table_name,
            data_stage=destination_connector.data_stage,
        )
        destination_connector.load(
            source_name=source_connector.name,
            source_table_name=source_table_name,
            data=data,
        )
        logger.info(
            f"Successfully ingested data from source: {source_connector.name} to destination: {destination_connector.name}"
        )

    def run(self):
        """Sequentially run all steps of the pipeline."""
        for source_connector in self.sources_connectors:
            sources_tables = self._get_tables_for_source(source_connector.name)
            logger.info(f"Starting extraction for source:{source_connector.name}:")
            for source_table_name in sources_tables:
                logger.info(
                    f"Extracting raw data for source:{source_connector.name} table:{source_table_name}.."
                )
                source_extract = source_connector.extract(source_table_name)
                logger.info(
                    f"Successfully extracted raw data from {source_connector.name} table:{source_table_name}."
                )
                for destination_connector in self.destinations_connectors:
                    self._process_extract_and_load(
                        source_extract,
                        source_table_name,
                        source_connector,
                        destination_connector,
                    )
            logger.info(f"Done ingesting data for source:{source_connector.name}")


def get_pipeline(pipeline_name: str) -> Pipeline:
    """Get pipeline object.

    Args:
        pipeline_name (str): Name of the pipeline defined in a configuration file

    Raises:
        ValueError: The pipeline can't be found

    Returns:
        Pipeline: Corresponding pipeline object
    """
    definitions = utils.get_definitions_from_file()
    pipelines = definitions.pipelines
    if pipeline_name not in [p.name for p in pipelines]:
        raise ValueError(f"{pipeline_name} pipeline does not exist")
    pipeline_config = list(filter(lambda p: p.name == pipeline_name, pipelines))[0]
    pipeline_obj = Pipeline(pipeline_config)
    return pipeline_obj
