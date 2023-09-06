from abc import ABC, abstractmethod


class DatabaseConnector(ABC):

    @abstractmethod
    def connect(self, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass
