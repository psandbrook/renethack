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

MS_PER_STEP = 1000.0 / 80.0
# How many milliseconds the simulation is updated by each step.

def start() -> None:
    """The main function of the game.
    
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
    # The default config to use if the config file does not exist.

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

    while True:
        start_time = get_millitime()

        # Update `lag` so it includes the new time that needs
        # to be processed:
        lag += elapsed
        
        while lag >= MS_PER_STEP:

            # While there's still a step's worth of time to be
            # processed, update the state and lag:
            state = state.step(MS_PER_STEP, config)
            lag -= MS_PER_STEP

            if state is None:

                # The state has exited, so stop the loop:
                return

            elif isinstance(state, tuple):

                # The state is requesting a config change.
                state_fn, config = state

                with open(config_path, mode='wb') as file:
                    pickle.dump(config, file)

                surface = renethack.config.apply(config)
                state = state_fn()

        state.render(surface)
        pygame.display.flip()

        # Set `elapsed` to the amount of time
        # that this iteration took. 
        elapsed = abs(get_millitime() - start_time)
