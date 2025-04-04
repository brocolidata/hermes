from hermes.exceptions import DestinationError

class ObjectStorageDestinationError(DestinationError):
    def __init__(self, name, path, error):
        self.connector_name = "Object Storage"
        self.error_message = f"""error while loading data to {name}, located at {path}.
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)
