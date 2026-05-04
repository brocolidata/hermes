import datetime as dt
from itertools import product
from typing import Any

import omegaconf
from croniter import croniter

from hermes import connectors
from hermes import exceptions as hermes_exceptions
from hermes import logging_utils, utils

logger = logging_utils.get_logger()


class Pipeline:
    """Represents a static data pipeline configuration."""

    def __init__(self, pipeline_config: omegaconf.dictconfig.DictConfig):
        self.pipeline_config = pipeline_config
        self.pipeline_name = pipeline_config.name
        self.schedule = pipeline_config.schedule
        self.sources_tables = self._get_sources_tables()
        self.destinations_names = pipeline_config.destinations
        self.sources_connectors = self._get_sources_connectors()
        self.destinations_connectors = self._get_destinations_connectors()

    def _get_sources_tables(self) -> dict[str, list]:
        dc_sources_tables_map = {}
        for dc_pipeline_source in self.pipeline_config.sources:
            dc_sources_tables_map[dc_pipeline_source.name] = dc_pipeline_source.tables
        return dc_sources_tables_map

    def _get_connector_names_by_metatype(self, connector_meta_type: str) -> list[str]:
        match connector_meta_type:
            case "source":
                return list(self.sources_tables.keys())
            case "destination":
                return self.destinations_names
        return []

    def _get_connector(self, connector_meta_type: str) -> list:
        definitions = utils.get_definitions_from_file()
        meta_type_plural = f"{connector_meta_type}s"
        connectors_configs = list(
            filter(
                lambda c: c.name in self._get_connector_names_by_metatype(connector_meta_type),
                definitions[meta_type_plural],
            )
        )
        return [
            connectors.get_connector(dc_connector, meta_type_plural)
            for dc_connector in connectors_configs
        ]

    def _get_sources_connectors(self) -> list:
        return self._get_connector("source")

    def _get_destinations_connectors(self) -> list:
        return self._get_connector("destination")

    def _get_window_from_schedule(self) -> dict:
        cron = croniter(self.schedule, dt.datetime.now())
        start_timestamp = cron.get_prev()
        end_timestamp = cron.next()
        return {"start_timestamp":start_timestamp, "end_timestamp":end_timestamp}
    
    def create_run(self, run_context: dict | None = None) -> "PipelineRun":
        """Factory method to create a new execution instance of this pipeline."""
        run_context = run_context or {}
        window = self._get_window_from_schedule()
        final_run_context = window | run_context 
        return PipelineRun(self, run_context=final_run_context)


class PipelineRun:
    """Manages the lifecycle and state of a single pipeline execution."""

    def __init__(self, pipeline: Pipeline, run_context: dict | None = None):
        self.pipeline = pipeline
        self.run_context = run_context or {}
        
        # Initialize run-specific state
        self.successes = []
        self.errors = []

    def _process_extract(self, source_extract: Any, source_connector: Any, source_table_name: str, data_stage: str):
        table_config = source_connector._get_table_config(source_table_name)
        data_key = table_config.get("data_key", "data")
        
        match data_stage:
            case "raw":
                return source_extract[data_key]
            case "processed":
                logger.info(f"Processing {source_connector.name} raw data..")
                output = source_connector.process_data(source_extract)
                logger.info(f"Successfully processed {source_connector.name} raw data")
                return output

    def _collect_error(self, source_name: str, table_name: str, dest_name: str, error: Exception):
        self.errors.append({
            "source_name": source_name,
            "source_table_name": table_name,
            "destination_name": dest_name,
            "error_type": type(error).__name__,
            "error_message": str(error).strip(),
            "run_context": self.run_context
        })

    def _execute_step(self, source_table_name: str, source_connector: Any, destination_connector: Any):
        """Internal method to handle a single table EL logic."""

        # 1. Extract
        try:
            logger.info(f"Extracting for source:{source_connector.name} table:{source_table_name}..")
            source_extract = source_connector.extract(source_table_name, self.run_context)
        except hermes_exceptions.SourceError as e:
            self._collect_error(source_connector.name, source_table_name, destination_connector.name, e)
            return

        # 2. Process & Load
        try:
            data = self._process_extract(
                source_extract, source_connector, source_table_name, destination_connector.data_stage
            )
            destination_connector.load(
                source_name=source_connector.name,
                source_table_name=source_table_name,
                data=data,
            )
            self.successes.append({
                "source_name": source_connector.name,
                "source_table_name": source_table_name,
                "destination_name": destination_connector.name,
            })
        except hermes_exceptions.DestinationError as e:
            self._collect_error(source_connector.name, source_table_name, destination_connector.name, e)

    def run(self):
        """Sequentially run all steps of this specific execution."""
        combinations = product(self.pipeline.sources_connectors, self.pipeline.destinations_connectors)
        
        for source_connector, destination_connector in combinations:
            logger.info(f"Starting run for source: {source_connector.name}")
            tables = self.pipeline.sources_tables.get(source_connector.name, [])
            for table_name in tables:
                self._execute_step(table_name, source_connector, destination_connector)
        
        return {"successes": self.successes, "errors": self.errors}


def get_pipeline(pipeline_name: str) -> Pipeline:
    definitions = utils.get_definitions_from_file()
    try:
        pipeline_config = list(filter(lambda p: p.name == pipeline_name, definitions.pipelines))[0]
        return Pipeline(pipeline_config)
    except IndexError:
        raise hermes_exceptions.PipelineError(
            name=pipeline_name,
            process_step="configuration retrieval",
            error=f"{pipeline_name} configuration cannot be found",
        )