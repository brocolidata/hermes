import json
import pathlib

import omegaconf
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from hermes import logging_utils, settings
from hermes.exceptions import ConfigLoadError

logger = logging_utils.get_logger()


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


def get_json_schema(file_name="json_schema"):
    JSON_SCHEMAS_FOLDER = pathlib.Path(
        pathlib.Path(__file__).parent.as_posix(), "json_schemas"
    )
    file_path = pathlib.Path(JSON_SCHEMAS_FOLDER, f"{file_name}.json")
    with open(file_path) as f:
        data = json.load(f)
    return data


def validate_definition_file(definitions):
    # dc_definitions = omegaconf.OmegaConf.to_container(definitions, resolve=True)
    json_schema = get_json_schema()
    try:
        validate(definitions, json_schema)
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

    except Exception as e:
        raise e
    finally:
        return config_is_valid
