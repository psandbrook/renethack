import pygame
from pygame import Surface

from renethack import world, entity
from renethack.gui import Label, Button, WorldDisplay
from renethack.world import make_world
from renethack.entity import Hero
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
            font_type='serif'
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

    # return: 'State'|None
    def step(self, ms_per_step: int):
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

        self.hero = entity.rand_hero('Hero')

        self.world = make_world(
            levels=LEVELS,
            level_length=LEVEL_LENGTH,
            hero=self.hero
            )

        self.world_display = WorldDisplay(self.world)
        self.components = [self.world_display]

    # return: 'State'|None
    def step(self, ms_per_step: int):
        """Step the game state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):

                # If escape is pressed, return to the main menu:
                return MainMenu()

            else:

                for c in self.components:
                    c.check_event(event)

                self.hero.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.hero.energy < 100 or len(self.hero.actions) > 0:
            # If we're not waiting for input, step the world:
            self.world = world.step(self.world)

        # If we are waiting for input, don't step the world.

        return self

    def render(self, surface: Surface) -> None:
        """Render the current game state."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)
