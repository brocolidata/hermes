from hermes.exceptions import DestinationError

class AthenaIcebergDestinationError(DestinationError):
    def __init__(self, glue_database, glue_table, table_location, temp_path, error):
        self.connector_name = "Athena Iceberg"
        self.error_message = f"""error while loading data to {glue_database}.{glue_table}.
            table location: {table_location}, temp path: {temp_path}
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)
