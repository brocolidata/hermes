import re

from omegaconf import OmegaConf, dictconfig

from hermes import connectors, utils
from hermes.exceptions import ConfigLoadError


def process_destination_variable_kwargs(
    ls_destination_variables: list, table_name: str, pipeline_cache
) -> dictconfig.DictConfig:
    dc_destination_variables = OmegaConf.create(
        {
            destination_variable: fetch_destination_variable(
                destination_variable, table_name
            )
            for destination_variable in ls_destination_variables
            if destination_variable not in pipeline_cache
        }
    )

    return dc_destination_variables


def fetch_destination_variable(destination_variable: str, table_name: str) -> dict:
    destination_config, variable_name, variable_config = (
        fetch_destination_and_variable_config(destination_variable)
    )
    destination_connector = connectors.get_connector(destination_config, "destinations")
    extract = destination_connector.get_destination_variable(
        variable_name, variable_config, table_name
    )
    return extract


def fetch_destination_and_variable_config(destination_variable: str) -> tuple:
    try:
        destination_name, variable_name = parse_destination_string(destination_variable)
        definitions = utils.get_definitions_from_file()
        destination_config = list(
            filter(lambda d: d.name == destination_name, definitions.destinations)
        )[0]
        variable_config = destination_config.variables[variable_name]
        return destination_config, variable_name, variable_config
    except Exception as e:
        raise ConfigLoadError(
            process_step=f"loading {destination_variable} destination variable",
            error=str(e),
        )


def parse_destination_string(destination_variable: str) -> tuple:
    try:
        DESTINATION_VARIABLE_PATTERN = r"^\$destinations.(?P<destination_name>\w*).variables.(?P<variable_name>\w*)$"
        matches = re.match(DESTINATION_VARIABLE_PATTERN, destination_variable)
        destination_name = matches.group("destination_name")
        variable_name = matches.group("destination_name")
        return destination_name, variable_name

    except AttributeError as e:
        raise ConfigLoadError(
            process_step="destination variable string parsing", error=str(e)
        )
