import json
import logging
import pathlib
from importlib.metadata import entry_points

import omegaconf
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from hermes import settings
from hermes.exceptions import ConfigLoadError

logger = logging.getLogger()


def get_hermes_connectors() -> list[str]:
    """
    List all available Hermes connectors by querying entry points.

    Returns:
         list[str]: List of all connectors.
    """
    connectors = {"sources": [], "destinations": []}
    try:
        source_entry_points = entry_points(group="hermes_plugins.sources")
        connectors["sources"] = list(source_entry_points.names)

        destination_entry_points = entry_points(group="hermes_plugins.destinations")
        connectors["destinations"] = list(destination_entry_points.names)
        hermes_connectors = []
        for connector_type in connectors.keys():
            for connector in connectors[connector_type]:
                connector_name = (
                    f"{connector}_{connector_type[:-1]}"  # [:-1] to remove the last 's'
                )
                hermes_connectors.append(connector_name)
        logging.info(f"Found {len(hermes_connectors)} Hermes connectors")
        return hermes_connectors

    except Exception as e:
        logger.error(f"Error retrieving Hermes connectors: {e}")


def load_and_merge_configs(user_config_path):
    config_path = user_config_path or settings.get_config_folder()
    merged_config = omegaconf.OmegaConf.create(
        {"sources": [], "destinations": [], "pipelines": []}
    )
    for config_file_path in config_path.rglob("*.yml"):
        yaml_config = omegaconf.OmegaConf.load(config_file_path)
        for key in ["sources", "destinations", "pipelines"]:
            if key in yaml_config:
                merged_config[key].extend(yaml_config[key])

    definitions = omegaconf.OmegaConf.to_container(merged_config, resolve=True)
    logger.info("Definition files successfully loaded and merged")
    return definitions


def write_definitions(definitions, artefact_path):
    if artefact_path:
        artifact_file_path = pathlib.Path(artefact_path, "definitions.json")
    else:
        artifact_file_path = settings.get_definition_file_path()
    if artifact_file_path.exists():
        logger.info(f"Overwriting existing {settings.HERMES_DEFINITIONS_FILE}")
    elif not artifact_file_path.parent.exists():
        artifact_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(artifact_file_path, "w") as f:
        json.dump(definitions, f, indent=2)
    logger.info(f"Artifact successfully written to {artifact_file_path}")


def get_json_schema(file_name="json_schema"):
    JSON_SCHEMAS_FOLDER = pathlib.Path(
        pathlib.Path(__file__).parent.as_posix(), "json_schemas"
    )
    file_path = pathlib.Path(JSON_SCHEMAS_FOLDER, f"{file_name}.json")
    with open(file_path) as f:
        data = json.load(f)
    return data


def validate_definition_file(definitions):
    json_schema = get_json_schema()
    try:
        validate(definitions, json_schema)
        logger.info("Configuration is valid")
    except ValidationError as e:
        raise ConfigLoadError(
            process_step="validation of YAML definitions",
            error=str(e),
        )


def parse_project(user_config_path=None, artefact_path=None):
    config_is_valid = False
    try:
        # Generate definitions
        definitions = load_and_merge_configs(user_config_path)

        # Validate definitions
        validate_definition_file(definitions)

        # Write definitions
        write_definitions(definitions, artefact_path)

        # Make sure environment variables are defined
        _ = settings.get_config_folder()
        _ = settings.get_artifacts_folder()
        _ = settings.get_custom_connectors_folder()
        config_is_valid = True
        logger.info("Parsing successful !")
    except Exception as e:
        logger.error(f"An error occurred during project parsing: {e}")
        raise e
    finally:
        return config_is_valid
