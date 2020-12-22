from abc import ABC, abstractmethod
from typing import TypeVar


class BaseFilter(ABC):
    @abstractmethod
    def __init__(self):
        ...

    def dict(self):
        return {key: value for key, value in self.__dict__.items() if value}


FilterType = TypeVar('FilterType', bound=BaseFilter)


def get_filter_order_params(filter_obj: FilterType, extra_params: dict):
    filter_params = {**filter_obj.dict(), **extra_params}
    if 'order' in filter_params:
        order = filter_params.pop('order')
    else:
        order = None
    return filter_params, order
