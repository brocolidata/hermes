import abc
import pathlib
import typing
from runpy import run_path

import pandas as pd

from hermes import settings
from hermes.sources.utils import BaseSource


class CustomSource(BaseSource):
    """Custom source connector."""

    def __init__(self, source_config):
        """Create an instance of the connector

        Args:
            source_config (omegaconf.dictconfig.DictConfig): configuration for the source
        """
        self.name = source_config.name
        self.description = source_config.description
        self.config = source_config.config
        self.output_tables = source_config.config.tables
        self.extractor_obj = self._get_extractor()

    def _get_table_config(self, table_name):
        table_config = list(filter(lambda t: t.name == table_name, self.output_tables))[
            0
        ]
        return table_config

    def _get_extractor(self) -> typing.Callable:
        """Get entrypoint function for the source connector

        Raises:
            ValueError: The function can't be found in the module

        Returns:
            function: Source connector entrypoint function
        """
        extractor_name = self.config.extractor
        module_file_path = self.config.module_path
        custom_connectors_path = settings.get_custom_connectors_folder()
        module_path = pathlib.Path(custom_connectors_path, module_file_path)
        module_obj = run_path(module_path)
        extractor_obj = module_obj.get(extractor_name)
        if not extractor_obj:
            raise ValueError(
                f"{extractor_name} function cannot be found in {module_path.as_posix()}"
            )
        return extractor_obj

    def extract(self, source_table) -> dict[str, pd.DataFrame]:
        """Extract data from the source

        Returns:
            dict[str, pd.DataFrame]: Data extracted from the source
        """
        table_config = self._get_table_config(source_table)
        kwargs = table_config.kwargs
        extractor = self.extractor_obj()
        dc_outputs = extractor.extract(**kwargs)
        return dc_outputs

    def process_data(self, dc_outputs):
        extractor = self.extractor_obj()
        processed_data = extractor.process_data(dc_outputs)
        return processed_data


class CustomSourceExtractor(abc.ABC):
    @abc.abstractmethod
    def extract():
        return NotImplemented

    @abc.abstractmethod
    def process_data(raw_data: dict) -> dict[str, pd.DataFrame]:
        return NotImplemented
