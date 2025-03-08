import abc


class BaseDestination(abc.ABC):
    @abc.abstractmethod
    def load():
        return NotImplemented
