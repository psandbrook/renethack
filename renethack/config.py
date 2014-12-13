import os
import collections
import pickle

import pygame

OPENGL_FLAG = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.OPENGL

Config = collections.namedtuple('Config', 'fullscreen resolution')

def apply(config):
    """Apply the given config and return the resultant surface object.

    `pygame.display.set_mode` is used to apply the config.
    """
    fullscreen_flag = pygame.FULLSCREEN if config.fullscreen else 0
    return pygame.display.set_mode(
        config.resolution,
        fullscreen_flag | OPENGL_FLAG
        )

def write_to(path, config):
    """Write the config object to the file at `path`."""
    with open(path, mode='wb') as file:
        pickle.dump(file)

def read_from(path, default):
    """Return a Config object read from the file at `path`.

    If the file is not found, `default` is returned instead.
    """
    if os.path.exists(path):
        with open(path, mode='rb') as file:
            return pickle.load(file)
    else:
        return default
