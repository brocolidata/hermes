import json
import pathlib
from functools import lru_cache

import omegaconf

from hermes import logging_utils, settings

logger = logging_utils.get_logger()


def load_config(file_name: str) -> omegaconf.dictconfig.DictConfig:
    """Load config from file

    Args:
        file_name (str): file path relative to HERMES_CONFIG_FOLDER

    Returns:
        omegaconf.dictconfig.DictConfig: config object
    """
    config_path = settings.get_config_folder()
    config_file_path = pathlib.Path(config_path, file_name)
    config = omegaconf.OmegaConf.load(config_file_path)
    return config


def load_definitions() -> dict[str, dict]:
    """"""
    config_path = pathlib.Path(settings.get_config_folder())
    ls_node_types = [n.value for n in settings.NodeTypes]
    dc_definitions = {
        element:{} for element in ls_node_types
    }
    for config_file_path in config_path.rglob('*.yml'):
        config_file = omegaconf.OmegaConf.load(config_file_path)
        for element in ls_node_types:
            if element in config_file:
                for element_dc in getattr(config_file, element):
                    if (element_name := element_dc.name) in dc_definitions["sources"]:
                        raise ValueError(
                            f"The {element_name} {element[:-1]} is already defined"
                        )
                    else:
                        dc_definitions[element][element_name] = config_file_path.as_posix()
    return dc_definitions


# @lru_cache
# def load_node_from_file(file_path, node_type, node_name):
#     file_config = omegaconf.OmegaConf.load(file_path)
#     node_config = file_config.get(node_type).get(node_name)
#     return node_config


def write_definitions():
    """Write definitions.yml artifact
    """
    dc_definitions = load_definitions()
    artifact_file_path = settings.get_definition_file_path()
    # ls_node_types = [n.value for n in settings.NodeTypes]
    # dc_all_nodes = {
    #     element:{} for element in ls_node_types
    # }
    # for node_type in dc_definitions:
    #     for node_name, file_path in dc_definitions.get(node_type).items():
    #         node_config = load_node_from_file(file_path, node_type, node_name)
    #         dc_all_nodes[node_type][node_name] = node_config
    if artifact_file_path.exists():
        logger.info(f'Overwriting existing {settings.HERMES_DEFINITIONS_FILE}')
    elif not artifact_file_path.parent.exists():
        artifact_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(artifact_file_path, 'w') as f:
        json.dump(dc_definitions, f)


def get_definitions_from_file() -> omegaconf.dictconfig.DictConfig:
    definition_file_path = settings.get_definition_file_path()
    definitions = omegaconf.OmegaConf.load(definition_file_path)
    return definitions


def parse_project():
    # load_node_from_file.cache_clear()
    write_definitions()

