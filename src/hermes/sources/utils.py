import abc

class BaseSource(abc.ABC):

    @abc.abstractmethod
    def extract():
        return NotImplemented