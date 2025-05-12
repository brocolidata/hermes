from hermes.exceptions import DestinationError, DestinationVariableError

CONNECTOR_NAME = "Athena Iceberg"
class AthenaIcebergDestinationError(DestinationError):
    def __init__(
        self, glue_database, glue_table, table_location, temp_path, process_step, error
    ):
        self.connector_name = CONNECTOR_NAME
        self.error_message = f"""error during {process_step} {glue_database}.{glue_table}.
            table location: {table_location}, temp path: {temp_path}
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)

class AthenaIcebergDestinationVariableError(DestinationVariableError):
    def __init__(
        self, glue_database, glue_table, variable_name, process_step, error
    ):
        self.connector_name = CONNECTOR_NAME
        self.error_message = f"""error during {process_step} of variable {variable_name} linked to {glue_database}.{glue_table}.
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)
