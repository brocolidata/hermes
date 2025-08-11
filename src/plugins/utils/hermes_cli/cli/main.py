def get_connectors() -> list[str]:
    """Retrieve a list of available connectors from pyproject.toml."""
    connectors = [
        "custom_source",
        "athena_iceberg_destination",
        "generic_object_storage_destination",
        "s3_destination",
        "local_storage_destination",
        "hermes_artefact_parser",
    ]
    return connectors
