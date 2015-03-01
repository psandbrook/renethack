import pygame
from pygame import Surface

import renethack
from renethack.gui import Label, Button, WorldDisplay, StatusDisplay, MessageDisplay
from renethack.entity_types import Hero, Wait
from renethack.util import validate

LEVELS = 10
LEVEL_LENGTH = 30

class MainMenu:

    def __init__(self) -> None:
        """Initialise the main menu to the default state."""

        self.title_label = Label(
            pos=(0.5, 0.1),
            height=0.2,
            text='ReNetHack',
            font_type='serif',
            alignment='centre'
            )

        self.newgame_button = Button(
            pos=(0.5, 0.3),
            width=0.4,
            height=0.1,
            text='New Game'
            )

        self.exit_button = Button(
            pos=(0.5, 0.5),
            width=0.4,
            height=0.1,
            text='Exit'
            )

        self.components = [
            self.title_label,
            self.newgame_button,
            self.exit_button
            ]

    def step(self, ms_per_step: float):
        """Step this main menu state."""
        validate(self.step, locals())

        for event in pygame.event.get():
            # For each input event, check if it's a quit event
            # and then pass the event through each component.

            if event.type == pygame.QUIT:
                # If this is a quit event,
                # return `None` immediately.
                return None

            else:
                for c in self.components:
                    c.check_event(event)

        # Now that the input events have been checked,
        # step each component:
        for c in self.components:
            c.step(ms_per_step)

        if self.exit_button.pressed:
            return None
        if self.newgame_button.pressed:
            return MainGame()
        else:
            # If nothing has happened, keep this main menu:
            return self

    def render(self, surface: Surface) -> None:
        """Render this main menu to the given surface."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        # Clear the screen to black.

        for c in self.components:
            c.render(surface)

class MainGame:

    def __init__(self) -> None:
        """Initialise this object to its default state."""

        self.hero = renethack.entity.rand_hero('Hero')

        self.world = renethack.world.make_world(
            levels=LEVELS,
            level_length=LEVEL_LENGTH,
            hero=self.hero
            )

        self.world_display = WorldDisplay(
            pos=(0.5, 0.5),
            width=0.6,
            height=1.0,
            world=self.world
            )

        self.status_display = StatusDisplay(
            pos=(0.1, 0.5),
            height=0.25,
            hero=self.hero
            )

        self.message_display = MessageDisplay(
            pos=(0.9, 0.5),
            width=0.2,
            height=1.0
            )

        self.components = [
            self.world_display,
            self.status_display,
            self.message_display
            ]

    def step(self, ms_per_step: float):
        """Step the game state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    # If escape is pressed, return to the main menu:
                    return MainMenu()

                elif event.key == pygame.K_SPACE:
                    self.hero.wait()

            else:

                for c in self.components:
                    # Pass on event to each component.
                    c.check_event(event)

        for c in self.components:
            # Update each component.
            c.step(ms_per_step)

        # Check if a tile has been clicked.
        if self.world_display.pressed is not None:
            self.hero.path_to(self.world, self.world_display.pressed)

        if self.hero.energy < 100 or len(self.hero.actions) > 0:
            # Update the world if not waiting for input.
            renethack.world.step(self.world)

        return self

    def render(self, surface: Surface) -> None:
        """Render the current game state."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)
