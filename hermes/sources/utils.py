import abc


class BaseSource(abc.ABC):
    @abc.abstractmethod
    def extract():
        return NotImplemented

    @abc.abstractmethod
    def _get_table_config(self, source_table_name: str) -> dict:
        """Look up table configuration for the given source table name.

        Returns a dict-like object containing table configuration (e.g. data_key).
        Subclasses must implement this to provide per-table metadata.
        """
        return NotImplemented
