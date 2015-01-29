import pygame
from pygame import Surface
from pygame.event import EventType

from renethack.util import validate

class Label:

    # pos: (int, int)
    def __init__(
            self,
            pos: tuple,
            height: int,
            text: str,
            font_type: str) -> None:

        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

        self.pos = (surface_w * pos_x, surface_h * pos_y)

        self.font = pygame.font.Font(
            pygame.font.match_font(font_type),
            int(surface_h * height)
            )
        # Create a font with the correct font type and height.

        self.text = text

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: int) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        font_render = self.font.render(self.text, True, (255, 255, 255))

        centre_xoffset = font_render.get_width() / 2
        centre_yoffset = font_render.get_height() / 2
        centre_x, centre_y = self.pos

        surface.blit(
            font_render,
            (centre_x - centre_xoffset, centre_y - centre_yoffset)
            )

class Button:

    # pos: (int, int)
    def __init__(
            self,
            pos: tuple,
            width: int,
            height: int,
            text: str) -> None:
        """Create a button that is displayed on screen.

        `pos`, `width` and `height` are values between 0 and 1.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

        self.rect = pygame.Rect(
            surface_w * (pos_x - width / 2),
            surface_h * (pos_y - height / 2),
            surface_w * width,
            surface_h * height
            )
        # Create a rectangle with the correct top-left position.

        self.text = text

        self.font = pygame.font.Font(
            pygame.font.match_font('sans'),
            int(self.rect.height * 0.8)
            )
        # Set the font to be sans and have a height of 80%
        # of the rectangle height.

        self.hover = False
        self.pressed = False

    def check_event(self, event: EventType) -> None:
        """Update this button using `event`."""
        validate(self.check_event, locals())

        if event.type == pygame.MOUSEMOTION:

            if self.rect.collidepoint(event.pos):
                # If the mouse pointer is colliding with this button:
                self.hover = True

            else:
                self.hover = False

        elif (event.type == pygame.MOUSEBUTTONDOWN
                and self.rect.collidepoint(event.pos)
                and event.button == 1):

            # If this button has been clicked:
            self.pressed = True
            self.pressed_this_step = True

    def step(self, ms_per_step: int) -> None:
        """Step this button by `ms_per_step`."""
        validate(self.step, locals())

        if self.pressed:

            if self.pressed_this_step:
                # If this button was clicked in this step:
                self.pressed_this_step = False

            else:
                # If this button was clicked last step:
                self.pressed = False
                del self.pressed_this_step

    def render(self, surface: Surface) -> None:
        """Render this button to the given surface."""
        validate(self.render, locals())

        # Draw the rectangle with the correct colour:
        colour = (38, 68, 102) if self.hover else (78, 78, 78)
        surface.fill(colour, self.rect)

        font_render = self.font.render(
            self.text,
            True,
            (255, 255, 255),
            colour
            )

        centre_xoffset = font_render.get_width() / 2
        centre_yoffset = font_render.get_height() / 2
        centre_x, centre_y = self.rect.center

        surface.blit(
            font_render,
            (centre_x - centre_xoffset, centre_y - centre_yoffset)
            )

class WorldDisplay:

    # world: ([Level], Level, [Level])
    def __init__(self, world: tuple) -> None:
        """Initialise this display with `world`."""
        validate(self.__init__, locals())

        self.world = world

    def check_event(self, event: EventType) -> None:
        """Update this component using `event`."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: int) -> None:
        """Step this component by `ms_per_step`."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this display to the given surface."""
        validate(self.render, locals())
