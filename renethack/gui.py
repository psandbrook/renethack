import os
import itertools
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

RESOLUTIONS = [(800, 600), (1280, 1024), (1366, 768), (1920, 1080)]
# The list of valid resolutions for the game window.

class Label:
    """Fixed text that is always visible."""

    def __init__(
            self,
            pos: tuple,
            height: float,
            text: str,
            font_type: str,
            alignment: str,
            colour: tuple) -> None:
        """Initialise a new `Label` object.

        pos: a pair of floats that describe this label's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the label.
        font_type: the font family of the text.
        alignment: the alignment of the text in relation to the
            position. Valid values are 'centre' and 'left'.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos

        self.pos = (surface_w * pos_x, surface_h * pos_y)

        self.font = Font(
            pygame.font.match_font(font_type),
            int(surface_h * height)
            )

        self.text = text
        self.alignment = alignment
        self.colour = colour

    # A `Label` object has no need to check for events or update
    # itself, so `check_event` and `step` are empty.

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this label to the given surface."""
        validate(self.render, locals())

        font_render = self.font.render(self.text, True, self.colour)
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
        """Initialise a new `Button` object.

        pos: a pair of floats that describe this buttons's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        width: the normalized width of the button.
        height: the normalized height of the button.
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
        # The rectangle that will be displayed on the screen to
        # indicate the area that can be clicked.

        self.text = text

        self.font = Font(
            pygame.font.match_font('sans'),
            int(self.rect.height * 0.8)
            )

        self.hover = False
        # Whether the button is being hovered over.

        self.pressed = False
        # Whether the button has been clicked.

    def check_event(self, event: EventType) -> None:
        """Update this button using `event`."""
        validate(self.check_event, locals())

        # If the mouse is located inside the rectangle, set `self.hover`
        # to `True`, else set it to `False`. If there is a click inside
        # the rectangle, set `self.hover` to `True`.

        if event.type == pygame.MOUSEMOTION:

            if self.rect.collidepoint(event.pos):
                self.hover = True

            else:
                self.hover = False

        elif (event.type == pygame.MOUSEBUTTONDOWN
                and self.rect.collidepoint(event.pos)
                and event.button == 1):

            self.pressed = True

            self.pressed_this_step = True
            # Set a temporary variable to track which step the click
            # event occured.

    def step(self, ms_per_step: float) -> None:
        """Step this button by `ms_per_step`."""
        validate(self.step, locals())

        # Only set `self.pressed` to `False` if the click event
        # happened during the last step, not this one.

        if self.pressed:

            if self.pressed_this_step:
                self.pressed_this_step = False

            else:
                self.pressed = False
                del self.pressed_this_step

    def render(self, surface: Surface) -> None:
        """Render this button to the given surface."""
        validate(self.render, locals())

        colour = (38, 68, 102) if self.hover else (78, 78, 78)
        surface.fill(colour, self.rect)

        font_render = self.font.render(
            self.text,
            True,
            (255, 255, 255),
            colour
            )

        x_offset = font_render.get_width() / 2
        y_offset = font_render.get_height() / 2
        x, y = self.rect.center

        surface.blit(font_render, (x - x_offset, y - y_offset))

class Image:
    """Displays an image loaded from a file."""

    def __init__(self, filename: str, pos: tuple, height: float) -> None:
        """Initialise a new `Image` object.

        pos: a pair of floats that describe this image's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the image.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        raw_img = pygame.image.load(filename)

        # When resizing the image to fit `height`, the image ratio must
        # be preserved.

        height_px = surface_h * height
        width_px = height_px / (raw_img.get_height() / raw_img.get_width())

        self.top_left = (
            surface_w*pos_x - width_px/2,
            surface_h*pos_y - height_px/2
            )

        self.image = pygame.transform.scale(
            raw_img,
            (int(width_px), int(height_px))
            )

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this element to the given surface."""
        validate(self.render, locals())

        surface.blit(self.image, self.top_left)

class TextBox:
    """Displays text in a box that the user has input."""

    def __init__(self, pos: tuple, height: float) -> None:
        """Initialise a new `TextBox` object.

        pos: a pair of floats that describe this text box's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the text box.
        """
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

        # The text of the label must be updated each step, so
        # initially it is set empty.

        self.label = Label(
            pos=pos,
            height=height*0.8,
            text='',
            font_type='sans',
            alignment='centre',
            colour=(255, 255, 255)
            )

    def get_text(self) -> str:
        """Returns the text of the label."""
        return self.label.text

    def check_event(self, event: EventType) -> None:
        """Check `event` with this element."""
        validate(self.check_event, locals())

        # If backspace is pressed, the last character must be removed.
        # If any other key is pressed, add its character to the label.

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self.label.text = self.label.text[:-1]

            else:
                self.label.text += event.unicode

    def step(self, ms_per_step: float) -> None:
        """Update this element."""
        validate(self.step, locals())

    def render(self, surface: Surface) -> None:
        """Render this element to the given surface."""
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
        """Initialise a new `WorldDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        width: the normalized width of the display.
        height: the normalized height of the display.
        world: the `World` object to be displayed.
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

        self.world = world
        level_length = len(world.current_level.tiles)
        rect_width, rect_height = self.rect.size

        self.tile_length = min(
            rect_width // level_length,
            rect_height // level_length
            )

        def icon_entries() -> GeneratorType:
            """Generates a dict of names to tile icons."""

            icon_dir = os.path.join(get_maindir(), 'data', 'icons')

            # All of the image files in the icons directory must be
            # loaded into a map of icon names to `Surface` objects.

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

        def y_rects(x: int) -> GeneratorType:
            """Generates the `x`th column of rectangles."""
            validate(y_rects, locals())

            display_botleft_x, display_botleft_y = self.rect.bottomleft

            # For each row, a column of rectangles must be generated.

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
        # A grid of rectangles that represent each tile in the current
        # level.

        self.hover = None
        # The co-ordinates of the tile that the mouse is positioned
        # over, or `None` if the mouse is outside of the world
        # display area.

        self.pressed = None
        # The co-ordinates of the tile that the mouse has clicked, or
        # `None` if a tile has not been clicked.

    def check_event(self, event: EventType) -> None:
        """Update this component using `event`."""
        validate(self.check_event, locals())

        level_length = len(self.world.current_level.tiles)

        # If there is a mouse motion or click event, set `self.hover`
        # and `self.pressed` to the correct values.

        if event.type == pygame.MOUSEMOTION:

            for x in range(level_length):
                for y in range(level_length):

                    if self.tile_rects[x][y].collidepoint(event.pos):
                        self.hover = (x, y)
                        return

            self.hover = None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            for x in range(level_length):
                for y in range(level_length):

                    if self.tile_rects[x][y].collidepoint(event.pos):
                        self.pressed = (x, y)
                        self.pressed_this_step = True
                        return

    def step(self, ms_per_step: float) -> None:
        """Step this component by `ms_per_step`."""
        validate(self.step, locals())

        # Only set `self.pressed` to `None` if the click event happened
        # during the last step, not this one.

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

        # Render each tile in the level using the appropriate icon.

        for x in range(level_length):
            for y in range(level_length):

                tile = self.world.current_level.tiles[x][y]
                rect = self.tile_rects[x][y]

                if tile.entity is not None:
                    icon = self.icons[tile.entity.icon_name].copy()
                else:
                    icon = self.icons[tile.type.name].copy()

                # If the tile is being hovered over, highlight it.

                if self.hover == (x, y):
                    colourise(icon, (64, 64, 64))

                surface.blit(icon, rect)

class StatusDisplay:
    """Displays the hero's status."""

    def __init__(self, pos: tuple, width: float, hero: Hero) -> None:
        """Initialise a new `StatusDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        width: the normalized width of the display.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        height = width*1.25
        top_pos = pos_y - height/2
        left_pos = pos_x - width/2
        text_height = height*0.1

        # Generate a sequence of labels, each with the same x position
        # and a different y position.
        labels = (
            Label(
                pos=(left_pos, top_pos + height*x),
                height=text_height,
                text='',
                font_type='mono',
                alignment='left',
                colour=(255, 255, 255)
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

    def __init__(self, pos: tuple, width: float, height: float) -> None:
        """Initialise a new `MessageDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        width: the normalized width of the display.
        height: the normalized height of the display.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        self.left_pos = pos_x - width/2
        top_pos = pos_y - height/2

        self.messages = []
        line_height = height*0.03
        self.font_height = line_height*0.8

        # Because a message may be of an arbitrary length, there must
        # be a mechanism that wraps the text and displays it on
        # multiple lines.

        # A monospace font family must be used because a constant
        # character width is required.
        font = Font(
            pygame.font.match_font('mono'),
            int(surface_h * self.font_height)
            )

        font_px_width, _ = font.size('a')
        self.chars_per_line = int(surface_w * width / font_px_width)
        self.lines = int(surface_h * height / (surface_h * line_height))

        # The possible y positions for labels must be saved for use
        # in the render function.

        self.y_positions = list(
            xrange(
                top_pos + line_height/2,
                top_pos + line_height*self.lines,
                line_height
                )
            )

    def add_message(self, msg: str) -> None:
        """Add a message to the end of the message list."""
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

        # Any messages that are over the character limit must be split
        # onto multiple lines.
        self.messages = [
            str_
            for msg in self.messages
            for str_ in textwrap.wrap(msg, width=self.chars_per_line)
            ]

        # If there are too many lines of messages, remove the ones at
        # the beginning of the list.
        while len(self.messages) > self.lines:
            del self.messages[0]

        # The colour of each line must be toggled between white and
        # grey to allow each line to be more easily distinguished.

        colours = itertools.cycle([(255, 255, 255), (190, 190, 190)])
        seq = zip(self.messages, self.y_positions, colours)

        for msg, y_pos, colour in seq:

            label = Label(
                pos=(self.left_pos, y_pos),
                height=self.font_height,
                text=msg,
                font_type='mono',
                alignment='left',
                colour=colour
                )

            label.render(surface)

class ScoreDisplay:
    """Displays a character's score."""

    def __init__(self, pos: tuple, height: float, score: Score) -> None:
        """Initialise a new `ScoreDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the display.
        """
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
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=pos,
                height=text_height,
                text='Level: {}'.format(score.level),
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(pos_x, pos_y + line_height),
                height=text_height,
                text='Score: {}'.format(score.score),
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
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

    def __init__(self, pos: tuple, height: float) -> None:
        """Initialise a new `ResolutionDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the display.
        """
        validate(self.__init__, locals())

        pos_x, pos_y = pos
        width = height*6
        button_offset = width*0.075

        self.left_button = Button(
            pos=(pos_x - width/2 + button_offset, pos_y),
            width=width*0.15,
            height=height,
            text='<'
            )

        self.right_button = Button(
            pos=(pos_x + width/2 - button_offset, pos_y),
            width=width*0.15,
            height=height,
            text='>'
            )

        self.resolution_label = Label(
            pos=pos,
            height=height,
            text='',
            font_type='sans',
            alignment='centre',
            colour=(255, 255, 255)
            )

        self.components = [
            self.left_button,
            self.right_button,
            self.resolution_label
            ]

    def res_update(self, res: tuple) -> tuple:
        """
        Update this component using `res`. Returns the new resolution.
        """
        validate(self.res_update, locals())

        # If either button has been pressed, get the appropriate
        # resolution. Otherwise keep the current one.

        res_index = RESOLUTIONS.index(res)

        if self.left_button.pressed:
            res_index = min_clamp(res_index - 1, 0)

        elif self.right_button.pressed:
            res_index = max_clamp(res_index + 1, len(RESOLUTIONS) - 1)

        new_res = RESOLUTIONS[res_index]
        x, y = new_res
        self.resolution_label.text = '{}x{}'.format(x, y)
        return new_res

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

    def __init__(self, pos: tuple, height: float) -> None:
        """Initialise a new `VolumeDisplay` object.

        pos: a pair of floats that describe this display's position on
            the screen. The floats must be normalized, e.g. a value
            of (0.3, 0.6) means 30% of the screen width and 60% of
            the screen height. (0, 0) is the top left corner.
        height: the normalized height of the display.
        """
        validate(self.__init__, locals())

        surface_w, surface_h = pygame.display.get_surface().get_size()
        pos_x, pos_y = pos
        width = height*6
        button_width = 0.15
        bar_width = (1 - 2*button_width)/10
        bar_rect_width = bar_width*0.5
        self.bars = 0

        self.left_button = Button(
            pos=(pos_x - width*(0.5 - button_width/2), pos_y),
            width=width*button_width,
            height=height,
            text='<'
            )

        self.right_button = Button(
            pos=(pos_x + width*(0.5 - button_width/2), pos_y),
            width=width*button_width,
            height=height,
            text='>'
            )

        self.components = [self.left_button, self.right_button]

        # Generate a list of rectangles that represent the current
        # volume, depending on which rectangles are rendered.
        self.rects = [
            Rect(
                surface_w * (pos_x - width/2 + width*x),
                surface_h * (pos_y - height/2),
                surface_w * width * bar_rect_width,
                surface_h * height
                )
            for x in xrange(
                button_width + (bar_width - bar_rect_width)/2,
                1-button_width,
                bar_width
                )
            ]

    def vol_update(self, volume: float) -> float:
        """
        Update this component using `volume`. Returns the new volume.
        """
        validate(self.vol_update, locals())

        if self.left_button.pressed:
            volume = min_clamp(volume-0.1, 0.0)

        elif self.right_button.pressed:
            volume = max_clamp(volume+0.1, 1.0)

        self.bars = round(volume * 10)
        return volume

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

        for x in range(self.bars):
            surface.fill((255, 255, 255), self.rects[x])

def colourise(surface: Surface, rgb: tuple) -> Surface:
    """
    Returns the same surface with an rgb value added to all the pixels
    on it.
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
