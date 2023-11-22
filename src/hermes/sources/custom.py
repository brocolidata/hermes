import pathlib
from runpy import run_path
import typing

import omegaconf
import pandas as pd

from hermes import settings
from hermes.sources.utils import BaseSource


class CustomSource(BaseSource):
    """Custom source connector.
    """

    def __init__(self, source_config):
        """Create an instance of the connector

        Args:
            source_config (omegaconf.dictconfig.DictConfig): configuration for the source
        """
        self.name = source_config.name
        self.description = source_config.description
        self.config = source_config.config
        self.function_obj = self._get_function()

    
    def _get_function(self) -> typing.Callable:
        """Get entrypoint function for the source connector

        Raises:
            ValueError: The function can't be found in the module

        Returns:
            function: Source connector entrypoint function
        """
        function_name = self.config.function_name
        module_file_path = self.config.module_path
        custom_connectors_path = settings.get_custom_connectors_folder()
        module_path = pathlib.Path(custom_connectors_path, module_file_path)
        module_obj = run_path(module_path)
        function_obj = module_obj.get(function_name)
        if not function_obj:
            raise ValueError(
                f'{function_name} function cannot be found in {module_path.as_posix()}'
            )
        return function_obj

    
    def extract(self) -> dict[str, pd.DataFrame]:
        """Extract data from the source

        Returns:
            dict[str, pd.DataFrame]: Data extracted from the source
        """
        kwargs = self.config.kwargs
        outputs_dc = self.function_obj(**kwargs)
        return outputs_dc

        