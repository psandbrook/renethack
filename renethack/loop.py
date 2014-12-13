import os
import sys

import pygame

import renethack
from renethack.config import Config
from renethack.state import MainMenu

config_path = os.path.join(renethack.util.get_maindir(), 'config.dat')
# The path to the config file.

start_state = MainMenu()
# The state that is active when the game starts.

MS_PER_STEP = 1000.0 / 80.0
# How many milliseconds the simulation is updated by each step.

def main_loop():
    """The main loop of the game.
    
    This function initialises Pygame and runs the main loop
    until the user exits the program.
    """
    pygame.init()

    default_config = Config(
        fullscreen=False,
        resolution=(800, 600)
        )
    # The default config to use if the config file does not exist.

    config = renethack.config.read_from(config_path, default_config)
    screen = renethack.config.apply(config)

    state = start_state

    elapsed = 0.0
    # The amount of milliseconds that the last iteration took.

    lag = 0.0
    # The amount of milliseconds that the simulation
    # needs to be updated by.

    while True:
        start_time = renethack.util.get_millitime()

        # Update `lag` so it includes the new time that needs
        # to be processed:
        lag += elapsed
        
        while lag >= MS_PER_STEP:
            # While there's still a step's worth of time to be
            # processed, update the state and lag:
            state = state.step(MS_PER_STEP)
            lag -= MS_PER_STEP

            if state is None:
                # The state returns `None` if it has exited.
                break

        if state is None:
            break
        else:
            state.render(screen)
            pygame.display.flip()

            # Set `elapsed` to the amount of time
            # that this iteration took. 
            elapsed = renethack.util.get_millitime() - start_time
