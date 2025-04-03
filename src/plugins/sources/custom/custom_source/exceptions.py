from hermes.exceptions import SourceError

class CustomSourceError(SourceError):
    def __init__(self, name, process_step, error):
        self.connector_name = "Custom Source"
        self.error_message = f"""error during {process_step} for source {name}.
            error : {error}
        """
        super().__init__(self.connector_name, self.error_message)

