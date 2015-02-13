import sys
import os
import time
import random

def validate(func, args: dict) -> bool:
    """Tests whether the values in `args` have the correct types."""

    for name, type_ in func.__annotations__.items():
        if name != 'return' and not isinstance(args[name], type_):

            raise TypeError('argument {} = {}: expected {}, found {}'
                .format(
                    name,
                    args[name],
                    type_.__name__,
                    type(args[name]).__name__
                    )
                )

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

def forany(pred, list_: list) -> bool:
    """Tests whether a predicate holds for any element of the list."""
    validate(forany, locals())
    return any(map(pred, list_))

def rand_chance(prob: float) -> bool:
    """Randomly returns True or False based on `prob`."""
    validate(rand_chance, locals())
    return random.random() < prob

def raw_filename(path: str) -> str:
    """Returns the file name without any extension."""
    validate(raw_filename, locals())

    root, _ = os.path.splitext(path)
    return os.path.basename(root)

def clamp(value, min_, max_):
    """Returns a value that is within the given bounds.

    If `value` is already within the bounds, `value` is returned.
    """

    if value < min_:
        return min_

    elif value > max_:
        return max_

    else:
        return value
