import abc
import pathlib
import typing
from runpy import run_path

import omegaconf
import pandas as pd

from custom_source.exceptions import CustomSourceError
from hermes import settings
from hermes.sources.utils import BaseSource


class CustomSource(BaseSource):
    """Custom source connector."""

    def __init__(self, source_config: omegaconf.dictconfig.DictConfig):
        """Create an instance of the connector

        Args:
            source_config (omegaconf.dictconfig.DictConfig): configuration for the source
        """
        self.name = source_config.name
        self.description = source_config.description
        self.config = source_config.config
        self.output_tables = source_config.config.tables
        self.extractor_name = self.config.extractor
        self.module_file_path = self.config.module_path
        self.extractor_obj = self._get_extractor()
        self._kwargs_destination_variables_map = (
            self._map_output_tables_kwargs_to_destination_variables()
        )

    def _get_table_config(
        self, source_table_name: str
    ) -> omegaconf.dictconfig.DictConfig:
        """Get table configuration from output tables

        Args:
            source_table_name (str): name of the source table

        Raises:
            CustomSourceError: if the table configuration cannot be found

        Returns:
            omegaconf.dictconfig.DictConfig: table configuration
        """
        try:
            table_config = list(
                filter(lambda t: t.name == source_table_name, self.output_tables)
            )[0]
        except IndexError:
            raise CustomSourceError(
                name=self.name,
                process_step="extraction",
                error=f"{source_table_name} table configuration cannot be found in {self.name} output tables",
            )
        return table_config

    def _get_extractor(self) -> typing.Callable:
        """Get entrypoint function for the source connector

        Raises:
            CustomSourceError: if the extractor or its module cannot be found

        Returns:
            typing.Callable: source connector entrypoint function
        """
        custom_connectors_path = settings.get_custom_connectors_folder()["path"]
        module_path = pathlib.Path(custom_connectors_path, self.module_file_path)
        try:
            module_obj = run_path(module_path)
            extractor_obj = module_obj.get(self.extractor_name)
        except FileNotFoundError:
            raise CustomSourceError(
                name=self.name,
                process_step="initialization",
                error=f"{self.extractor_name} function cannot be found in {module_path.as_posix()}",
            )
        if not extractor_obj:
            raise CustomSourceError(
                name=self.name,
                process_step="initialization",
                error=f"{self.extractor_name} function cannot be found in {module_path.as_posix()}",
            )
        return extractor_obj

    def _map_output_tables_kwargs_to_destination_variables(self):
        dc_map = {}
        for output_table in self.output_tables:
            dc_map[output_table.name] = {
                kwak: (kwav if kwav.startswith("$destinations.") else None)
                for kwak, kwav in output_table.kwargs.items()
            }
        return dc_map

    def _process_table_kwargs(self, table_kwargs: dict, pipeline_cache: dict) -> dict:
        updated_table_kwargs = omegaconf.OmegaConf.create(
            {
                kwan: (
                    pipeline_cache[kwav] if kwav.startswith("$destinations.") else kwav
                )
                for kwan, kwav in table_kwargs
            }
        )
        return updated_table_kwargs

    def extract(
        self, source_table_name: str, pipeline_cache: dict = {}
    ) -> dict[str, typing.Any]:
        """Run the extract method of the custom extractor

        Args:
            source_table_name (str): name of the source table

        Raises:
            CustomSourceError: if any exception is raised during the call to the extract method

        Returns:
            dict[str, typing.Any]: outputs of the extract method, mapping of source table name to raw data
        """
        table_config = self._get_table_config(source_table_name)
        kwargs = (
            self._process_table_kwargs(table_config.kwargs, pipeline_cache)
            if pipeline_cache
            else table_config.kwargs
        )
        try:
            extractor = self.extractor_obj()
            dc_outputs = extractor.extract(**kwargs)
        except Exception as e:
            raise CustomSourceError(
                name=self.name, process_step="extracting", error=str(e)
            )
        return dc_outputs

    def process_data(self, dc_outputs: dict[str, typing.Any]) -> pd.DataFrame:
        """Run the process_data method of the custom extractor

        Args:
            dc_outputs (dict[str, typing.Any]): outputs of the extract method, mapping of source table name to raw data

        Raises:
            CustomSourceError: if any exception is raised during the call to the process_data method

        Returns:
            pd.DataFrame: processed data
        """
        try:
            extractor = self.extractor_obj()
            processed_data = extractor.process_data(dc_outputs)
        except Exception as e:
            raise CustomSourceError(
                name=self.name, process_step="data processing", error=str(e)
            )
        return processed_data


class CustomSourceExtractor(abc.ABC):
    @abc.abstractmethod
    def extract():
        return NotImplemented

    @abc.abstractmethod
    def process_data(raw_data: dict) -> dict[str, pd.DataFrame]:
        return NotImplemented
