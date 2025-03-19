from hermes.logging_utils import get_logger

logger = get_logger()


class HermesError(Exception):
    """Base class for all Hermes-related exceptions."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.log_error()

    def log_error(self):
        logger.error(self.message, exc_info=True)


class SourceError(HermesError):
    """Raised when there is an issue with data extraction."""

    def __init__(self, connector_name, error_message):
        self.connector_name = connector_name
        self.error_message = error_message
        self.message = self.get_message()
        super().__init__(self.message)

    def get_message(self):
        return f"{self.connector_name}: {self.error_message}"


class DestinationError(HermesError):
    """Raised when there is an issue with data loading."""

    def __init__(self, connector_name, error_message):
        self.connector_name = connector_name
        self.error_message = error_message
        self.message = self.get_message()
        super().__init__(self.message)

    def get_message(self):
        return f"{self.connector_name}: {self.error_message}"


class AthenaIcebergDestinationError(DestinationError):
    def __init__(self, glue_database, glue_table, table_location, temp_path, error):
        self.connector_name = "Athena Iceberg"
        self.error_message = f"""error while loading data to {glue_database}.{glue_table}.
            table location: {table_location}, temp path: {temp_path}
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)


class ObjectStorageDestinationError(DestinationError):
    def __init__(self, name, path, error):
        self.connector_name = "Object Storage"
        self.error_message = f"""error while loading data to {name}, located at {path}.
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)


class CustomSourceError(SourceError):
    def __init__(self, name, process_step, error):
        self.connector_name = "Custom Source"
        self.error_message = f"""error during {process_step} for source {name}.
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)


class PipelineError(HermesError):
    """Raised when there is a general pipeline execution failure."""

    def __init__(self, name, process_step, error):
        self.message = f"""error during {process_step} for pipeline {name}.
            error : {error}
        """
        super().__init__(self.message)


class ConfigLoadError(HermesError):
    """Raised when there is an issue loading a configuration file."""

    def __init__(self, process_step, error):
        self.message = f"""error during {process_step}.
            error : {error}
        """
        super().__init__(self.message)
