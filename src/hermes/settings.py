import enum
import os
import pathlib

HERMES_DEFINITIONS_FILE = "definitions.json"
GCS_PREFIX = "gs"


class ConnectorsMetaTypes(str, enum.Enum):
    source = "source"
    destination = "destination"


class ObjectStorageServicesPrefixes(str, enum.Enum):
    gcs = "gs"
    s3 = "s3"


class NodeTypes(str, enum.Enum):
    sources = "sources"
    destinations = "destinations"
    pipelines = "pipelines"


# def get_config_folder() -> str:
def get_config_folder() -> pathlib.Path:
    """Get the value of HERMES_CONFIG_FOLDER environment variable

    Raises:
        ValueError: HERMES_CONFIG_FOLDER environment variable isn't set

    Returns:
        pathlib.Path: The value of HERMES_CONFIG_FOLDER environment variable
    """
    hermes_config_folder = os.getenv("HERMES_CONFIG_FOLDER")
    if not hermes_config_folder:
        raise ValueError("HERMES_CONFIG_FOLDER environment variable must be set")
    else:
        return pathlib.Path(hermes_config_folder)


def get_artifacts_folder() -> str:
    """Get the value of HERMES_ARTIFACTS_FOLDER environment variable

    Raises:
        ValueError: HERMES_ARTIFACTS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_ARTIFACTS_FOLDER environment variable
    """
    hermes_artifacts_folder = os.getenv("HERMES_ARTIFACTS_FOLDER")
    if not hermes_artifacts_folder:
        raise ValueError("HERMES_ARTIFACTS_FOLDER environment variable must be set")
    else:
        return hermes_artifacts_folder


def get_custom_connectors_folder() -> str:
    """Get the value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable

    Raises:
        ValueError: HERMES_CUSTOM_CONNECTORS_FOLDER environment variable isn't set

    Returns:
        str: The value of HERMES_CUSTOM_CONNECTORS_FOLDER environment variable
    """
    hermes_custom_connectors_folder = os.getenv("HERMES_CUSTOM_CONNECTORS_FOLDER")
    if not hermes_custom_connectors_folder:
        raise ValueError(
            "HERMES_CUSTOM_CONNECTORS_FOLDER environment variable must be set"
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
