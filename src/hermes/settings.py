import enum
import os
import pathlib
from pathlib import Path

import yaml

from hermes.exceptions import ConfigLoadError

HERMES_DEFINITIONS_FILE = "definitions.json"


class ConnectorsMetaTypes(str, enum.Enum):
    source = "source"
    destination = "destination"


class ObjectStorageServicesPrefixes(str, enum.Enum):
    gcs = "gs:/"
    s3 = "s3:/"


class NodeTypes(str, enum.Enum):
    sources = "sources"
    destinations = "destinations"
    pipelines = "pipelines"


def generate_config_file():
    """Generate a configuration file for the Hermes CLI"""
    project_root = Path.cwd().resolve()
    config_file = project_root / "config.yml"
    config_file_content = {
        "project_paths": {
            "configuration_folder": "# equivalent of HERMES_CONFIG_FOLDER",
            "artifacts_folder": "# equivalent of HERMES_ARTIFACTS_FOLDER",
            "custom_connectors_folder": "# equivalent of HERMES_CUSTOM_CONNECTORS_FOLDER",
        }
    }
    with config_file.open("w") as f:
        yaml.safe_dump(config_file_content, f)


def load_config_file():
    """Load the configuration file for the Hermes CLI"""
    project_root = Path.cwd().resolve()
    config_file = project_root / "config.yml"
    if not config_file.exists():
        return "No configuration file found. Please generate one using 'hermes init'."

    with open(config_file, "r") as f:
        return yaml.safe_load(f) or {}


def get_config_folder() -> pathlib.Path:
    """Get the value of HERMES_CONFIG_FOLDER environment variable

    Raises:
        ConfigLoadError: if HERMES_CONFIG_FOLDER environment variable isn't set

    Returns:
        pathlib.Path: The value of HERMES_CONFIG_FOLDER environment variable
    """
    hermes_config_folder = os.getenv("HERMES_CONFIG_FOLDER")
    if hermes_config_folder:
        return pathlib.Path(hermes_config_folder)

    config = load_config_file()
    config_paths = config.get("project_paths", {})
    hermes_config_folder = config_paths.get("configuration_folder")

    if not hermes_config_folder:
        raise ConfigLoadError(
            process_step="access to Hermes configuration folder",
            error="HERMES_CONFIG_FOLDER environment variable must be set",
        )
    else:
        return pathlib.Path(hermes_config_folder)


def get_artifacts_folder() -> str:
    """Get the value of HERMES_ARTIFACTS_FOLDER environment variable

    Raises:
        ConfigLoadError: if HERMES_ARTIFACTS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_ARTIFACTS_FOLDER environment variable
    """
    hermes_artifacts_folder = os.getenv("HERMES_ARTIFACTS_FOLDER")
    if hermes_artifacts_folder:
        return hermes_artifacts_folder

    config = load_config_file()
    config_paths = config.get("project_paths", {})
    hermes_artefact_folder = config_paths.get("artifacts_folder")

    if not hermes_artefact_folder:
        raise ConfigLoadError(
            process_step="access to hermes artifact folder",
            error="HERMES_ARTIFACTS_FOLDER environment variable must be set",
        )
    else:
        return hermes_artifacts_folder


def get_custom_connectors_folder() -> str:
    """Get the value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable

    Raises:
        ConfigLoadError: HERMES_CUSTOM_CONNECTORS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable
    """
    hermes_custom_connectors_folder = os.getenv("HERMES_CUSTOM_CONNECTORS_FOLDER")
    # add retreive from fichier yml
    if not hermes_custom_connectors_folder:
        raise ConfigLoadError(
            process_step="access to custom connectors folder",
            error="HERMES_CUSTOM_CONNECTORS_FOLDER environment variable must be set",
        )
    else:
        return hermes_custom_connectors_folder


def get_definition_file_path() -> pathlib.Path:
    """Get the full path of Hermes definition file

    Returns:
        pathlib.Path: Full path of Hermes definition file
    """
    artifact_folder = get_artifacts_folder()
    definition_file_path = pathlib.Path(artifact_folder, HERMES_DEFINITIONS_FILE)
    return definition_file_path


### Logging messages
ATHENA_ICEBERG_ANTE_PROCESS_MSG = """
    Athena Iceberg: start loading data to {glue_database}.{glue_table}.
        table location: {table_location}, temp path: {temp_path}
"""
