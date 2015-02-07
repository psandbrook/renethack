import os

import pygame

import renethack
from renethack.config import Config
from renethack.state import MainMenu
from renethack.util import get_maindir, get_millitime

config_path = os.path.join(get_maindir(), 'config.dat')
# The path to the config file.

MS_PER_STEP = 1000.0 / 80.0
# How many milliseconds the simulation is updated by each step.

def start() -> None:
    """The main function of the game.
    
    This function initialises Pygame and runs the main loop
    until the user exits the program.
    """

    pygame.init()

    default_config = Config(
        fullscreen=False,
        resolution=(1366, 768)
        )
    # The default config to use if the config file does not exist.

    read_config = renethack.config.read_from(config_path, default_config)
    surface = renethack.config.apply(read_config)

    def main_loop() -> None:

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
                state = state.step(MS_PER_STEP)
                lag -= MS_PER_STEP

                if state is None:
                    # The state returns `None` if it has exited.
                    return

            state.render(surface)
            pygame.display.flip()

            # Set `elapsed` to the amount of time
            # that this iteration took. 
            elapsed = abs(get_millitime() - start_time)

    main_loop()
