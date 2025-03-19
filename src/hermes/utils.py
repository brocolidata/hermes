import functools
import json
import pathlib

import omegaconf
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from hermes import logging_utils, settings
from hermes.exceptions import ConfigLoadError

logger = logging_utils.get_logger()


def load_definitions() -> dict[str, dict]:
    """"""
    config_path = pathlib.Path(settings.get_config_folder())
    ls_node_types = [n.value for n in settings.NodeTypes]
    dc_definitions = {element: {} for element in ls_node_types}
    for config_file_path in config_path.rglob("*.yml"):
        config_file = omegaconf.OmegaConf.load(config_file_path)
        validate_definition_file(config_file)
        for element in ls_node_types:
            if element in config_file:
                for element_dc in getattr(config_file, element):
                    if (element_name := element_dc.name) in dc_definitions["sources"]:
                        raise ConfigLoadError(
                            process_step="YAML definitions loading",
                            error=f"The {element_name} {element[:-1]} is already defined",
                        )
                    else:
                        dc_definitions[element][element_name] = (
                            config_file_path.as_posix()
                        )
    return dc_definitions


def write_definitions():
    """Write definitions.yml artifact"""
    dc_definitions = load_definitions()
    artifact_file_path = settings.get_definition_file_path()
    if artifact_file_path.exists():
        logger.info(f"Overwriting existing {settings.HERMES_DEFINITIONS_FILE}")
    elif not artifact_file_path.parent.exists():
        artifact_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(artifact_file_path, "w") as f:
        json.dump(dc_definitions, f)


def get_definitions_from_file() -> omegaconf.dictconfig.DictConfig:
    definition_file_path = settings.get_definition_file_path()
    definitions = omegaconf.OmegaConf.load(definition_file_path)
    return definitions


def load_and_merge_configs():
    config_path = settings.get_config_folder()
    merged_config = omegaconf.OmegaConf.create(
        {"sources": [], "destinations": [], "pipelines": []}
    )

    for config_file_path in config_path.rglob("*.yml"):
        yaml_config = omegaconf.OmegaConf.load(config_file_path)
        for key in ["sources", "destinations", "pipelines"]:
            if key in yaml_config:
                merged_config[key].extend(yaml_config[key])

    artifact_file_path = settings.get_definition_file_path()
    if artifact_file_path.exists():
        logger.info(f"Overwriting existing {settings.HERMES_DEFINITIONS_FILE}")
    elif not artifact_file_path.parent.exists():
        artifact_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(artifact_file_path, "w") as f:
        json.dump(
            omegaconf.OmegaConf.to_container(merged_config, resolve=True), f, indent=2
        )


def get_json_schema(file_name="json_schema"):
    JSON_SCHEMAS_FOLDER = pathlib.Path(
        pathlib.Path(__file__).parent.as_posix(), "json_schemas"
    )
    file_path = pathlib.Path(JSON_SCHEMAS_FOLDER, f"{file_name}.json")
    with open(file_path) as f:
        data = json.load(f)
    return data


def validate_definition_file(definitions):
    dc_definitions = omegaconf.OmegaConf.to_container(definitions, resolve=True)
    json_schema = get_json_schema()
    try:
        validate(dc_definitions, json_schema)
    except ValidationError as e:
        raise ConfigLoadError(
            process_step="validation of YAML definitions",
            error=str(e),
        )


def parse_project():
    # Generate definitions
    load_and_merge_configs()

    # Make sure environment variables are defined
    _ = settings.get_config_folder()
    _ = settings.get_artifacts_folder()
    _ = settings.get_custom_connectors_folder()


def setup_project(func):
    """Parse project before running the wrapped function"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Parsing Hermes project...")
        parse_project()
        value = func(*args, **kwargs)
        return value

    return wrapper
