from itertools import product
import omegaconf
from hermes import connectors, utils, logging_utils
from hermes.destinations import variables
from hermes import exceptions as hermes_exceptions

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
        self._destination_variables_cache = omegaconf.OmegaConf.create({})
        self.successes = []
        self.errors = []

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
            connectors.get_connector(dc_connector, meta_type_plural)
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

    def _process_destination_variables(self, source_connector, source_table_name):
        try:
            destination_variables = source_connector._kwargs_destination_variables_map[
                source_table_name
            ]
            source_connector_is_using_destination_variables = any(
                destination_variables.values()
            )
            if source_connector_is_using_destination_variables:
                dc_destination_variables = (
                    variables.process_destination_variable_kwargs(
                        ls_destination_variables_str=list(
                            destination_variables.values()
                        ),
                        table_name=source_table_name,
                        pipeline_cache=self._destination_variables_cache,
                    )
                )
                self._destination_variables_cache.update(dc_destination_variables)

        except Exception as e:
            ...

    def _process_extract_and_load(
        self, source_table_name: str, source_connector: str, destination_connector: str
    ):
        """Extract, process, and load data from a source table to a destination.

        Args:
            source_table_name (str): name of the source table
            source_connector (str): source connector object
            destination_connector (str): destination connector object

        Raises:
            SourceError: if data extraction from the source fails
            DestinationError: if data loading to the destination fails

        Returns:
            None
        """

        # Process Destination variables if exists
        try:
            self._process_destination_variables(source_connector, source_table_name)
        except (hermes_exceptions.DestinationVariableError, hermes_exceptions.ConfigLoadError) as e:
            self._collect_errors(
                source_name=source_connector.name,
                source_table_name=source_table_name,
                destination_name=destination_connector.name,
                error=e,
            )
            return None

        # Extract data from source
        try:
            logger.info(
                f"Extracting raw data for source:{source_connector.name} table:{source_table_name}.."
            )
            source_extract = source_connector.extract(
                source_table_name, self._destination_variables_cache
            )
            logger.info(
                f"Successfully extracted raw data from {source_connector.name} table:{source_table_name}."
            )
        except hermes_exceptions.SourceError as e:
            self._collect_errors(
                source_name=source_connector.name,
                source_table_name=source_table_name,
                destination_name=destination_connector.name,
                error=e,
            )
            return None

        # Process data
        data = self._process_extract(
            source_extract=source_extract,
            source_connector=source_connector,
            source_table_name=source_table_name,
            data_stage=destination_connector.data_stage,
        )

        # Load data to destination
        try:
            destination_connector.load(
                source_name=source_connector.name,
                source_table_name=source_table_name,
                data=data,
            )
            logger.info(
                f"""Successfully ingested data from source: {source_connector.name} table:{source_table_name} 
                to destination: {destination_connector.name}"""
            )
            self.successes.append(
                {
                    "source_name": source_connector.name,
                    "source_table_name": source_table_name,
                    "destination_name": destination_connector.name,
                }
            )
        except hermes_exceptions.DestinationError as e:
            self._collect_errors(
                source_name=source_connector.name,
                source_table_name=source_table_name,
                destination_name=destination_connector.name,
                error=e,
            )

    def _collect_errors(
        self,
        source_name: str,
        source_table_name: str,
        destination_name: str,
        error: Exception,
    ):
        """Append an error to pipeline errors

        Args:
            source_name (str): name of the source
            source_table_name (str): name of the source table
            destination_name (str): name of the destination
            error (Exception): Exception raised
        """
        self.errors.append(
            {
                "source_name": source_name,
                "source_table_name": source_table_name,
                "destination_name": destination_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

    def run(self):
        """Sequentially run all steps of the pipeline."""
        source_destination_combinations = product(
            self.sources_connectors, self.destinations_connectors
        )
        for source_connector, destination_connector in source_destination_combinations:
            logger.info(f"Starting extraction for source:{source_connector.name}:")
            for source_table_name in self._get_tables_for_source(source_connector.name):
                self._process_extract_and_load(
                    source_table_name,
                    source_connector,
                    destination_connector,
                )


@utils.setup_project
def get_pipeline(pipeline_name: str) -> Pipeline:
    """Get pipeline object.

    Args:
        pipeline_name (str): Name of the pipeline defined in a configuration file

    Raises:
        PipelineError: The pipeline can't be found

    Returns:
        Pipeline: Corresponding pipeline object
    """
    definitions = utils.get_definitions_from_file()
    pipelines = definitions.pipelines
    try:
        pipeline_config = list(filter(lambda p: p.name == pipeline_name, pipelines))[0]
        pipeline_obj = Pipeline(pipeline_config)
    except IndexError:
        raise hermes_exceptions.PipelineError(
            name=pipeline_name,
            process_step="configuration retrieval",
            error=f"{pipeline_name} configuration cannot be found",
        )
    return pipeline_obj
