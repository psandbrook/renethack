import os
import collections
import pickle

import pygame
from pygame import Surface

from renethack.util import validate

Config = collections.namedtuple('Config', 'fullscreen resolution')
# fullscreen: bool
# resolution: (int, int)

def apply(config: Config) -> Surface:
    """Apply the given config and return the resultant surface object.

    `pygame.display.set_mode` is used to apply the config.
    """
    validate(apply, locals())

    # flag: int
    flag = (
        pygame.FULLSCREEN
        | pygame.HWSURFACE
        | pygame.DOUBLEBUF
        if config.fullscreen else 0
        )

    return pygame.display.set_mode(config.resolution, flag)

def write_to(path: str, config: Config) -> None:
    """Write the config object to the file at `path`."""
    validate(write_to, locals())

    with open(path, mode='wb') as file:
        pickle.dump(file)

def read_from(path: str, default: Config) -> Config:
    """Return a Config object read from the file at `path`.

    If the file is not found, `default` is returned instead.
    """
    validate(read_from, locals())

    if os.path.exists(path):
        with open(path, mode='rb') as file:
            return pickle.load(file)
    else:
        return default
