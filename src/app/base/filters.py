from abc import ABC, abstractmethod


class BaseFilter(ABC):
    @abstractmethod
    def __init__(self):
        ...

    def dict(self):
        return {key: value for key, value in self.__dict__.items() if value}