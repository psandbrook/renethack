import os
import pickle

import pygame

import renethack
from renethack.config import Config
from renethack.state import MainMenu
from renethack.util import get_maindir, get_millitime

config_path = os.path.join(get_maindir(), 'config.pickle')
# The path to the config file.

music_path = os.path.join(get_maindir(), 'data', 'music', 'Adventure Meme.ogg')
# The path to the music file.

MS_PER_STEP = 1000.0 / 80.0
# How many milliseconds the simulation is updated by each step.

def start() -> None:
    """The top level function of the game.

    This function initialises Pygame and runs the main loop
    until the user exits the program.
    """

    pygame.init()
    pygame.key.set_repeat(500, 10)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)

    default_config = Config(
        fullscreen=False,
        resolution=(1366, 768),
        volume=0.7
        )

    # If the config file does not exist, use the default config.

    if not os.path.exists(config_path):
        with open(config_path, mode='wb') as file:
            pickle.dump(default_config, file)

    with open(config_path, mode='rb') as file:
        config = pickle.load(file)

    surface = renethack.config.apply(config)
    state = MainMenu()

    elapsed = 0.0
    # The amount of milliseconds that the last iteration took.

    lag = 0.0
    # The amount of milliseconds that the simulation
    # needs to be updated by.

    # The main loop should always try to keep up with the real world
    # and only render when there is leftover time to do so.

    while True:
        start_time = get_millitime()

        # `lag` must be set to the new time that needs to be processed.
        lag += elapsed

        # The state must be updated until it catches up with the real
        # world.

        while lag >= MS_PER_STEP:

            state = state.step(MS_PER_STEP, config)
            lag -= MS_PER_STEP

            # If the state has exited, `state` will be `None`. If the
            # config needs to be changed, `state` will be a pair of
            # a function returning the new state and the new config.

            if state is None:
                return

            elif isinstance(state, tuple):
                state_fn, config = state

                with open(config_path, mode='wb') as file:
                    pickle.dump(config, file)

                surface = renethack.config.apply(config)
                state = state_fn()

        state.render(surface)
        pygame.display.flip()

        # `elapsed` must be set to the amount of time that this
        # iteration took.
        elapsed = abs(get_millitime() - start_time)
