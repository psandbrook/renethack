import sys
import os
import time
import random
from types import FunctionType

def validate(func, args: dict) -> bool:
    """Tests whether the values in `args` have the correct types."""

    params = {
        name: type_
        for name, type_ in func.__annotations__.items()
        if name != 'return'
        }

    for name, type_ in params.items():
        assert isinstance(args[name], type_)

def get_maindir() -> str:
    """
    Return the path to the directory that
    the '__main__' file is contained in.
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def get_millitime() -> float:
    """Return the current time in milliseconds.

    `time.monotonic` is used to get the time. The returned
    value may therefore be negative.
    """
    return time.monotonic() * 1000.0

# pred: a -> bool
# list_: [a]
def forany(pred: FunctionType, list_: list) -> bool:
    """Tests whether a predicate holds for any element of the list."""
    validate(forany, locals())
    return any(map(pred, list_))

def rand_chance(prob: float) -> bool:
    """Randomly returns True or False based on `prob`."""
    validate(rand_chance, locals())
    return random.random() < prob
