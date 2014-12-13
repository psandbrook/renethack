import sys

import pygame

class MainMenu:

    def __init__(self):
        # Initialise title and buttons:
        self.components = []

    def step(self, ms_per_step):
        """Step this main menu state."""

        for event in pygame.event.get():
            # For each input event, check if it's a quit event
            # and then pass the event through each component.

            if event.type == pygame.QUIT:
                # If this is a quit event,
                # return `None` immediately.
                return None

            for c in self.components:
                c.check_event(event)

        # Now that the input events have been checked,
        # step each component:
        for c in self.components:
            c.step(ms_per_step)

        return self
        # If nothing has happened, keep this main menu.

    def render(self, screen):
        """Render this main menu to the given screen."""
        for c in self.components:
            c.render(screen)
