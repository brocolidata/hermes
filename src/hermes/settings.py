import enum
import os
import pathlib
from pathlib import Path

import yaml

from hermes.exceptions import ConfigLoadError

HERMES_DEFINITIONS_FILE = "definitions.json"
HERMES_CONFIG_FILE = "hermes_config.yml"


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
    config_file = get_config_file_path()
    if not config_file.exists():
        return "No configuration file found. Please generate one using 'hermes init'."

    with open(config_file, "r") as f:
        return yaml.safe_load(f) or {}


def resolve_path_from_env_config(
    env_var_name: str,
    config_key: str,
    path_description: str,
    create_if_missing: bool = False,
) -> pathlib.Path:
    """
    Generic helper function to resolve a path from an environment variable or configuration file.
    Args:
        env_var_name (str): The name of the environment variable to check.
        config_key (str): The key in the configuration file to check if the environment variable is not set.
        path_description (str): A description of the path for error messages.
        create_if_missing (bool): If True, create the directory if it does not exist.
    Returns:
        pathlib.Path: The resolved path.
    Raises:
        ConfigLoadError: If the path cannot be resolved from either the environment variable or the configuration file.
    """
    #! 1. Try environment variable first (highest priority)
    env_path = os.getenv(env_var_name)
    if env_path:
        resolved_path = pathlib.Path(env_path)
        path = pathlib.Path(env_path)
        print(f"Using {env_var_name} environment variable: {resolved_path}")
    else:
        #! 2. Try config file
        try:
            config = load_config_file()
            config_paths = config.get("project_paths", {})
            config_path = config_paths.get(config_key)
            if not config_path:
                raise ConfigLoadError(
                    process_step=f"access to {path_description}",
                    error=f"{env_var_name} environment variable or '{config_key}' entry in {HERMES_CONFIG_FILE} must be set",
                )
            print(f"Using {config_key} from configuration file: {config_path}")
            path = pathlib.Path(config_path)
        except FileNotFoundError as e:
            raise ConfigLoadError(
                process_step=f"Load config from   {path_description}",
                error=f"Failed to load config file {HERMES_CONFIG_FILE}: {str(e)}",
            )
    #! 3. Resolve relative or absolute path
    if not path.is_absolute():
        path = pathlib.Path(Path.cwd(), path)

    path = path.resolve()

    if not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created {path_description} directory: {path}")
            except Exception as e:
                raise ConfigLoadError(
                    process_step=f"create {path_description}",
                    error=f"Failed to create directory '{path}': {str(e)}",
                )
        else:
            raise ConfigLoadError(
                process_step=f"access {path_description}",
                error=f"{path_description.title()} path '{path}' does not exist",
            )
    if not path.is_dir():
        raise ConfigLoadError(
            process_step=f"validate {path_description}",
            error=f"{path_description.title()} path '{path}' exists but is not a directory",
        )
    print(f"Successfully resolved {path_description}: {path}")
    return path


def get_config_file_path() -> pathlib.Path:
    """Get the full path of the Hermes configuration file"""
    project_root = Path.cwd().resolve()
    config_file = pathlib.Path(project_root, HERMES_CONFIG_FILE)
    if not config_file.exists():
        return None
    return config_file


def get_config_folder(create_if_missing: bool = False) -> pathlib.Path:
    """Get the value of HERMES_CONFIG_FOLDER environment variable

    Raises:
        ConfigLoadError: if HERMES_CONFIG_FOLDER environment variable isn't set

    Returns:
        pathlib.Path: The value of HERMES_CONFIG_FOLDER environment variable
    """
    path = resolve_path_from_env_config(
        env_var_name="HERMES_CONFIG_FOLDER",
        config_key="configuration_folder",
        path_description="Hermes configuration folder",
        create_if_missing=create_if_missing,
    )
    return path


def get_artifacts_folder(create_if_missing: bool = False) -> pathlib.Path:
    """Get the value of HERMES_ARTIFACTS_FOLDER environment variable

    Raises:
        ConfigLoadError: if HERMES_ARTIFACTS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_ARTIFACTS_FOLDER environment variable
    """
    return resolve_path_from_env_config(
        env_var_name="HERMES_ARTIFACTS_FOLDER",
        config_key="artefacts_folder",
        path_description="artifacts folder",
        create_if_missing=create_if_missing,
    )


def get_custom_connectors_folder(create_if_missing: bool = False) -> pathlib.Path:
    """Get the value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable

    Raises:
        ConfigLoadError: HERMES_CUSTOM_CONNECTORS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable
    """
    return resolve_path_from_env_config(
        env_var_name="HERMES_CUSTOM_CONNECTORS_FOLDER",
        config_key="custom_connectors_folder",
        path_description="custom connectors folder",
        create_if_missing=create_if_missing,
    )


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
