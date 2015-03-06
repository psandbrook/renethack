import os
import textwrap
from types import GeneratorType

import pygame
from pygame import Surface, PixelArray, Rect
from pygame.event import EventType
from pygame.font import Font

import renethack
from renethack.entity_types import Hero, Score
from renethack.world_types import World
from renethack.util import validate, get_maindir, raw_filename, clamp, min_clamp, max_clamp, xrange

RESOLUTIONS =[(800, 600), (1280, 1024), (1366, 768), (1920, 1080)]

class Label:
    """Fixed text that is always visible."""

    def __init__(
            self,
            pos: tuple,
            height: float,
            text: str,
            font_type: str,
            alignment: str) -> None:

        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

        self.pos = (surface_w * pos_x, surface_h * pos_y)

        self.font = Font(
            pygame.font.match_font(font_type),
            int(surface_h * height)
            )
        # Create a font with the correct font type and height.

        self.text = text
        self.alignment = alignment

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

        x, y = self.pos

        if self.alignment == 'centre':

            x_offset = font_render.get_width() / 2
            y_offset = font_render.get_height() / 2

        elif self.alignment == 'left':

            x_offset = 0
            y_offset = font_render.get_height() / 2

        else:
            raise ValueError('invalid alignment of {}'.format(self.alignment))

        surface.blit(font_render, (x - x_offset, y - y_offset))

class Button:
    """Displays text in a box and detects click events."""

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

        self.rect = Rect(
            surface_w * (pos_x - width / 2),
            surface_h * (pos_y - height / 2),
            surface_w * width,
            surface_h * height
            )
        # Create a rectangle with the correct top-left position.

        self.text = text

        self.font = Font(
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

class TextBox:
    """Displays text in a box that the user has input."""

    def __init__(
            self,
            pos: tuple,
            height: float) -> None:

        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        width = height*5
        left_pos = pos_x - width/2
        top_pos = pos_y - height/2

        self.underline_rect = Rect(
            surface_w * left_pos,
            surface_h * (top_pos + height*1.2),
            surface_w * width,
            surface_h * height * 0.05
            )

        self.label = Label(
            pos=pos,
            height=height*0.8,
            text='',
            font_type='sans',
            alignment='centre'
            )

    def get_text(self) -> str:
        return self.label.text

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self.label.text = self.label.text[:-1]

            else:
                self.label.text += event.unicode

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        surface.fill((255, 255, 255), self.underline_rect)
        self.label.render(surface)

class WorldDisplay:
    """Displays a `World` using a grid of rectangles."""

    def __init__(
            self,
            pos: tuple,
            width: float,
            height: float,
            world: World) -> None:
        """Initialise this display with `world`."""
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

        self.rect = Rect(
            surface_w * (pos_x - width / 2),
            surface_h * (pos_y - height / 2),
            surface_w * width,
            surface_h * height
            )
        # Create a rectangle with the correct top-left position.

        self.world = world
        level_length = len(world.current_level.tiles)

        rect_width, rect_height = self.rect.size

        self.tile_length = min(
            rect_width // level_length,
            rect_height // level_length
            )
        # Calculate the length of each tile in pixels.

        def icon_entries() -> GeneratorType:
            """Generates a dict of names to tile icons."""

            icon_dir = os.path.join(get_maindir(), 'data', 'icons')

            for file in os.listdir(icon_dir):

                _, ext = os.path.splitext(file)

                if ext.lower() == '.png':

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
            """Generates the `x`th column of rectangles."""
            validate(y_rects, locals())

            display_botleft_x, display_botleft_y = self.rect.bottomleft

            for y in range(level_length):

                topleft_x = display_botleft_x + self.tile_length*x
                topleft_y = display_botleft_y - self.tile_length * (y + 1)

                yield Rect(
                    topleft_x,
                    topleft_y,
                    self.tile_length,
                    self.tile_length
                    )

        self.tile_rects = [list(y_rects(x)) for x in range(level_length)]
        # A grid of rectangles that indicate where each tile should
        # be rendered.

        self.hover = None
        self.pressed = None

    def check_event(self, event: EventType) -> None:
        """Update this component using `event`."""
        validate(self.check_event, locals())

        level_length = len(self.world.current_level.tiles)

        if event.type == pygame.MOUSEMOTION:

            for x in range(level_length):
                for y in range(level_length):

                    if self.tile_rects[x][y].collidepoint(event.pos):
                        self.hover = (x, y)
                        return

            self.hover = None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            self.pressed_this_step = True

            for x in range(level_length):
                for y in range(level_length):

                    if self.tile_rects[x][y].collidepoint(event.pos):
                        self.pressed = (x, y)
                        return

    def step(self, ms_per_step: float) -> None:
        """Step this component by `ms_per_step`."""
        validate(self.step, locals())

        if self.pressed is not None:

            if self.pressed_this_step:
                self.pressed_this_step = False

            else:
                self.pressed = None
                del self.pressed_this_step

    def render(self, surface: Surface) -> None:
        """Render this display to the given surface."""
        validate(self.render, locals())

        level_length = len(self.world.current_level.tiles)

        # Render the level tile by tile:
        for x in range(level_length):
            for y in range(level_length):

                tile = self.world.current_level.tiles[x][y]
                rect = self.tile_rects[x][y]

                if tile.entity is not None:
                    # If there is an entity on the tile,
                    # render it instead:

                    icon = self.icons[tile.entity.icon_name].copy()

                else:
                    icon = self.icons[tile.type.name].copy()

                if self.hover == (x, y):
                    colourise(icon, (64, 64, 64))

                surface.blit(icon, rect)

class StatusDisplay:
    """Displays the hero's status."""

    def __init__(
            self,
            pos: tuple,
            width: float,
            hero: Hero) -> None:

        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        height = width*1.25
        top_pos = pos_y - height/2
        left_pos = pos_x - width/2
        text_height = height*0.1

        labels = (
            Label(
                pos=(left_pos, top_pos + height*x),
                height=text_height,
                text='',
                font_type='mono',
                alignment='left'
                )
            for x in xrange(1/14, 1, 1/7)
            )

        self.name_label = next(labels)
        self.score_label = next(labels)
        self.level_label = next(labels)
        self.hp_label = next(labels)
        self.defence_label = next(labels)
        self.speed_label = next(labels)
        self.strength_label = next(labels)

        self.components = [
            self.name_label,
            self.score_label,
            self.level_label,
            self.hp_label,
            self.defence_label,
            self.speed_label,
            self.strength_label
            ]

        self.hero = hero

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

        self.name_label.text = self.hero.name
        self.score_label.text = 'Score: {}'.format(self.hero.score)
        self.level_label.text = 'Level {}'.format(self.hero.level)

        self.hp_label.text = 'Hit Points: {}/{}'.format(
            self.hero.hit_points, self.hero.max_hit_points)

        self.defence_label.text = 'Defence: {}'.format(self.hero.defence)
        self.speed_label.text = 'Speed: {}'.format(self.hero.speed)
        self.strength_label.text = 'Strength: {}'.format(self.hero.strength)

    def render(self, surface: Surface) -> None:
        """Render this element to the given surface."""
        validate(self.render, locals())

        for c in self.components:
            c.render(surface)

class MessageDisplay:
    """Displays game messages."""

    def __init__(
            self,
            pos: tuple,
            width:float,
            height: float) -> None:

        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        self.left_pos = pos_x - width/2
        top_pos = pos_y - height/2

        self.messages = []
        line_height = height*0.04
        self.font_height = line_height*0.8

        font = Font(
            pygame.font.match_font('mono'),
            int(surface_h * self.font_height)
            )

        font_px_width, _ = font.size('a')
        self.chars_per_line = int(surface_w * width / font_px_width)
        self.lines = int(surface_h * height / (surface_h * line_height))

        self.y_positions = list(
            xrange(
                top_pos + line_height/2,
                top_pos + line_height*self.lines,
                line_height
                )
            )

    def add_message(self, msg: str) -> None:
        validate(self.add_message, locals())
        self.messages.append(msg)

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this element to the given surface."""
        validate(self.render, locals())

        self.messages = [
            str_
            for msg in self.messages
            for str_ in textwrap.wrap(msg, width=self.chars_per_line)
            ]

        if len(self.messages) > self.lines:
            del self.messages[:len(self.messages) - self.lines + 1]

        for msg, y_pos in zip(self.messages, self.y_positions):

            label = Label(
                pos=(self.left_pos, y_pos),
                height=self.font_height,
                text=msg,
                font_type='mono',
                alignment='left'
                )

            label.render(surface)

class ScoreDisplay:
    """Displays a character's score."""

    def __init__(
            self,
            pos: tuple,
            height: float,
            score: Score) -> None:

        validate(self.__init__, locals())

        pos_x, pos_y = pos
        line_height = height/3
        text_height = line_height*0.8
        self.components = []

        self.components.append(
            Label(
                pos=(pos_x, pos_y - line_height),
                height=text_height,
                text='Name: {}'.format(score.name),
                font_type='sans',
                alignment='left'
                )
            )

        self.components.append(
            Label(
                pos=pos,
                height=text_height,
                text='Level: {}'.format(score.level),
                font_type='sans',
                alignment='left'
                )
            )

        self.components.append(
            Label(
                pos=(pos_x, pos_y + line_height),
                height=text_height,
                text='Score: {}'.format(score.score),
                font_type='sans',
                alignment='left'
                )
            )

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        for c in self.components:
            c.render(surface)

class ResolutionDisplay:
    """Displays the resolution and provides controls to chage it."""

    def __init__(
            self,
            pos: tuple,
            height: float) -> None:

        validate(self.__init__, locals())

        pos_x, pos_y = pos
        width = height*6
        button_offset = width*0.1

        self.left_button = Button(
            pos=(pos_x - width/2 + button_offset, pos_y),
            width=width*0.2,
            height=height,
            text='<'
            )

        self.right_button = Button(
            pos=(pos_x + width/2 - button_offset, pos_y),
            width=width*0.2,
            height=height,
            text='>'
            )

        self.resolution_label = Label(
            pos=pos,
            height=height,
            text='',
            font_type='sans',
            alignment='centre'
            )

        self.components = [
            self.left_button,
            self.right_button,
            self.resolution_label
            ]

    def res_update(self, res: tuple) -> tuple:
        """
        Update this component using `res`. Returns
        the new resolution.
        """
        validate(self.res_update, locals())

        res_index = RESOLUTIONS.index(res)

        if self.left_button.pressed:
            res_index = min_clamp(res_index - 1, 0)

        elif self.right_button.pressed:
            res_index = max_clamp(res_index + 1, len(RESOLUTIONS) - 1)

        res = RESOLUTIONS[res_index]
        x, y = res
        self.resolution_label.text = '{}x{}'.format(x, y)
        return res

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

        for c in self.components:
            c.check_event(event)

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

        for c in self.components:
            c.step(ms_per_step)

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        for c in self.components:
            c.render(surface)

class VolumeDisplay:
    """Displays the volume and provides controls to change it."""

    def __init__(
            self,
            pos: tuple,
            height: float) -> None:

        validate(self.__init__, locals())

        #surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

def colourise(surface: Surface, rgb: tuple) -> Surface:
    """
    Returns the same surface with an rgb value added
    to all the pixels on it.
    """
    validate(colourise, locals())

    r, g, b = rgb
    pixels = PixelArray(surface)

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):

            px_colour = surface.unmap_rgb(pixels[x][y])
            new_r = clamp(px_colour.r + r, 0, 255)
            new_g = clamp(px_colour.g + g, 0, 255)
            new_b = clamp(px_colour.b + b, 0, 255)

            pixels[x][y] = (new_r, new_g, new_b)

    return pixels.surface
