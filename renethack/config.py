import collections

import pygame
from pygame import Surface

import renethack
from renethack.util import validate

Config = collections.namedtuple('Config', 'fullscreen resolution volume')
# fullscreen: bool
# resolution: (int, int)
# volume: float

def apply(config: Config) -> Surface:
    """Apply the given config and return the resulting surface object.

    `pygame.display.set_mode` is used to apply the config.
    """
    validate(apply, locals())

    flag = (
        pygame.FULLSCREEN
        | pygame.HWSURFACE
        | pygame.DOUBLEBUF
        if config.fullscreen else 0
        )

    pygame.mixer.music.set_volume(config.volume)
    return pygame.display.set_mode(config.resolution, flag)
