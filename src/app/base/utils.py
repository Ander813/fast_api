import random
from typing import Union


def random_sign(signs: Union[str, list[str]]):
    return random.choice(signs)