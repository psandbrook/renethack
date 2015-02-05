import os
from types import GeneratorType

import pygame
from pygame import Surface, PixelArray
from pygame.event import EventType

from renethack.entity_types import Hero
from renethack.util import validate, get_maindir, raw_filename, clamp

class Label:

    # pos: (float, float)
    def __init__(
            self,
            pos: tuple,
            height: float,
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

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        font_render = self.font.render(
            self.text,
            True,
            (255, 255, 255)
            )

        centre_xoffset = font_render.get_width() / 2
        centre_yoffset = font_render.get_height() / 2
        centre_x, centre_y = self.pos

        surface.blit(
            font_render,
            (centre_x - centre_xoffset, centre_y - centre_yoffset)
            )

class Button:

    # pos: (float, float)
    def __init__(
            self,
            pos: tuple,
            width: float,
            height: float,
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

    def step(self, ms_per_step: float) -> None:
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

    # pos: (float, float)
    # world: ([Level], Level, [Level])
    def __init__(
            self,
            pos: tuple,
            width: float,
            height: float,
            world: tuple) -> None:
        """Initialise this display with `world`."""
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

        self.world = world
        _, level, _ = self.world
        level_length = len(level.tiles)

        rect_width, rect_height = self.rect.size

        self.tile_length = min(
            rect_width // level_length,
            rect_height // level_length
            )
        # Calculate the length of each tile in pixels.

        def icon_entries():

            icon_dir = os.path.join(get_maindir(), 'data', 'icons')

            for file in os.listdir(icon_dir):

                full_path = os.path.join(icon_dir, file)
                name = raw_filename(file)

                icon = pygame.transform.scale(
                    pygame.image.load(full_path),
                    (self.tile_length, self.tile_length)
                    )

                yield name, icon

        self.icons = dict(icon_entries())
        # Create a dictionary of names to `Surface` objects.

        def y_rects(x: int) -> GeneratorType:
            validate(y_rects, locals())

            display_botleft_x, display_botleft_y = self.rect.bottomleft

            for y in range(level_length):

                topleft_x = display_botleft_x + self.tile_length*x
                topleft_y = display_botleft_y - self.tile_length * (y + 1)

                yield pygame.Rect(
                    topleft_x,
                    topleft_y,
                    self.tile_length,
                    self.tile_length
                    )

        self.tile_rects = [list(y_rects(x)) for x in range(level_length)]
        # A list of rectangles that indicate where each tile should
        # be rendered.

        self.hover = None

    def check_event(self, event: EventType) -> None:
        """Update this component using `event`."""
        validate(self.check_event, locals())

        _, level, _ = self.world
        level_length = len(level.tiles)

        if event.type == pygame.MOUSEMOTION:

            for x in range(level_length):
                for y in range(level_length):

                    if self.tile_rects[x][y].collidepoint(event.pos):
                        self.hover = (x, y)
                        return

            self.hover = None


    def step(self, ms_per_step: float) -> None:
        """Step this component by `ms_per_step`."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this display to the given surface."""
        validate(self.render, locals())

        _, level, _ = self.world
        level_length = len(level.tiles)

        # Render the level tile by tile:
        for x in range(level_length):
            for y in range(level_length):

                tile = level.tiles[x][y]
                rect = self.tile_rects[x][y]

                if tile.entity is not None:
                    # If there is an entity on the tile,
                    # render it instead:

                    if isinstance(tile.entity, Hero):
                        icon = self.icons['Hero'].copy()

                    else:
                        icon = self.icons[tile.entity.name].copy()

                else:
                    icon = self.icons[tile.type.name].copy()

                if self.hover == (x, y):
                    icon = colourise(icon, (64, 64, 64))

                surface.blit(icon, rect)

def colourise(surface: Surface, rgb: tuple) -> Surface:
    """
    Return a new surface with an rgb value added
    to all the pixels on it.
    """
    validate(colourise, locals())

    r, g, b = rgb
    pixels = PixelArray(surface.copy())

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):

            px_colour = surface.unmap_rgb(pixels[x][y])
            new_r = clamp(px_colour.r + r, 0, 225)
            new_g = clamp(px_colour.g + g, 0, 225)
            new_b = clamp(px_colour.b + b, 0, 225)

            pixels[x][y] = (new_r, new_g, new_b)

    return pixels.surface
