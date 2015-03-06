import collections

import pygame
from pygame import Surface

import renethack
from renethack.util import validate

Config = collections.namedtuple('Config', 'fullscreen resolution volume')
# fullscreen: bool
# resolution: (int, int)

def apply(config: Config) -> Surface:
    """Apply the given config and return the resultant surface object.

    `pygame.display.set_mode` is used to apply the config.
    """
    validate(apply, locals())

    flag = (
        pygame.FULLSCREEN
        | pygame.HWSURFACE
        | pygame.DOUBLEBUF
        if config.fullscreen else 0
        )

    return pygame.display.set_mode(config.resolution, flag)
