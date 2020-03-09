import os
import pickle

import pygame
from pygame import Surface

import renethack
from renethack.config import Config
from renethack.gui import Label, Button, Image, TextBox, WorldDisplay, StatusDisplay, MessageDisplay, ScoreDisplay, ResolutionDisplay, VolumeDisplay
from renethack.entity_types import Hero, Score
from renethack.util import validate, xrange, get_maindir

LEVELS = 10
# The number of levels in each game.

LEVEL_LENGTH = 30
# The length of each side of a level.

scores_path = os.path.join(get_maindir(), 'scores.pickle')
# The path to the scores file.

class MainMenu:
    """The main menu of the game.

    Displays the title of the game and a list of buttons that lead to
    the other parts of the program. Also displays the music credits
    in the bottom left corner.
    """

    def __init__(self) -> None:
        """Initialise a new `MainMenu` object."""

        # The buttons must have the same x position but different y
        # positions.

        button_y_pos = xrange(0.28, 1, 0.12)

        self.newgame_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.08,
            text='New Game'
            )

        self.instructions_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.08,
            text='How To Play'
            )

        self.scores_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.08,
            text='High Scores'
            )

        self.options_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.08,
            text='Options'
            )

        self.exit_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.08,
            text='Exit'
            )

        self.components = [
            self.newgame_button,
            self.instructions_button,
            self.scores_button,
            self.options_button,
            self.exit_button
            ]

        self.components.append(
            Label(
                pos=(0.5, 0.1),
                height=0.2,
                text='ReNetHack',
                font_type='serif',
                alignment='centre',
                colour=(255, 255, 255)
                )
            )

        credit_y_pos = xrange(0.84, 1, 0.03)

        self.components.append(
            Label(
                pos=(0.03, next(credit_y_pos)),
                height=0.03,
                text='Music:',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.03, next(credit_y_pos)),
                height=0.03,
                text='"Adventure Meme"',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.03, next(credit_y_pos)),
                height=0.03,
                text='Kevin MacLeod (incompetech.com)',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.03, next(credit_y_pos)),
                height=0.03,
                text='Licensed under Creative Commons: By Attribution 3.0',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.03, next(credit_y_pos)),
                height=0.03,
                text='http://creativecommons.org/licenses/by/3.0/',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

    def step(self, ms_per_step: float, config: Config):
        """Update this main menu state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:
                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        # If a button has been pressed, return the appropriate new
        # state. Otherwise, return this main menu.

        if self.exit_button.pressed:
            return None

        elif self.newgame_button.pressed:
            return NewGame()

        elif self.instructions_button.pressed:
            return HowToPlay()

        elif self.scores_button.pressed:
            return HighScores()

        elif self.options_button.pressed:
            return Options()

        else:
            return self

    def render(self, surface: Surface) -> None:
        """Render this main menu to the given surface."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

class NewGame:
    """The state that shows when a new game is to be started.

    A name for the player character can be entered. Pressing the
    enter key starts the game.
    """

    def __init__(self) -> None:
        """Initialise a new `NewGame` object."""
        validate(self.__init__, locals())

        self.back_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Back'
            )

        self.text_box = TextBox(pos=(0.5, 0.5), height=0.1)
        self.components = [self.back_button, self.text_box]

        self.components.append(
            Label(
                pos=(0.5, 0.2),
                height=0.1,
                text='Enter name:',
                font_type='serif',
                alignment='centre',
                colour=(255, 255, 255)
                )
            )

    def step(self, ms_per_step: float, config: Config):
        """Update this state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        for event in pygame.event.get():

            # If the enter key has been pressed, return a new
            # `MainGame` state using the name currently in the text
            # box.

            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return MainGame(self.text_box.get_text())

            for c in self.components:
                c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.back_button.pressed:
            return MainMenu()

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

class MainGame:
    """The state where the main game is played.

    A 2D grid of tiles is shown that represents the current level that
    the hero is on. The user can click on a tile to allow their
    character to perform certain actions. A list of messages and the
    character's stats are also shown to the sides of the screen.
    """

    def __init__(self, name: str) -> None:
        """Initialise this object to its default state."""
        validate(self.__init__, locals())

        self.score_saved = False
        self.hero = renethack.entity.rand_hero(name)

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

        self.exit_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Exit'
            )

        self.message_display = MessageDisplay(
            pos=(0.9, 0.5),
            width=0.18,
            height=1.0
            )

        self.components = [
            self.world_display,
            self.exit_button,
            self.message_display
            ]

        self.components.append(
            StatusDisplay(
                pos=(0.1, 0.5),
                width=0.18,
                hero=self.hero
                )
            )

    def step(self, ms_per_step: float, config: Config):
        """Step the game state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        for event in pygame.event.get():

            # If the space key has been pressed, make the hero wait.

            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.hero.wait()

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.exit_button.pressed:

            if not self.score_saved:
                self.save_score()

            return MainMenu()

        for msg in self.hero.collect_messages():
            self.message_display.add_message(msg)

        if self.hero.hit_points > 0:

            if self.world_display.pressed is not None:
                self.hero.path_to(self.world, self.world_display.pressed)

            # The world must only be updated if the hero has less than
            # 100 energy or the hero has actions queued.

            if self.hero.energy < 100 or len(self.hero.actions) > 0:
                renethack.world.step(self.world)

        elif not self.score_saved:
            self.save_score()

        return self

    def save_score(self) -> None:

        self.score_saved = True
        scores = load_scores()

        scores.append(
            Score(
                name=self.hero.name,
                level=self.hero.level,
                score=self.hero.score
                )
            )

        scores.sort(key=lambda s: s.score, reverse=True)
        scores = scores[:3]

        with open(scores_path, 'wb') as file:
            pickle.dump(scores, file)

    def render(self, surface: Surface) -> None:
        """Render the current game state."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

class HowToPlay:
    """The state that shows instructions for the game.

    A list of instructions is shown. Each instruction may have an
    associated image.
    """

    def __init__(self) -> None:
        """Initialise this state."""

        self.back_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Back'
            )

        self.components = [self.back_button]

        self.components.append(
            Label(
                pos=(0.5, 0.1),
                height=0.15,
                text='How To Play',
                font_type='serif',
                alignment='centre',
                colour=(255, 255, 255)
                )
            )

        # Each label's associated image must have the same y position
        # but a different x position. All of the labels must have the
        # same x position and all of the images must have the same x
        # position.

        text_height = 0.06
        image_height = text_height*1.4
        y_positions = list(xrange(0.25, 1, text_height*1.8))

        def icon(name):
            return os.path.join(
                get_maindir(),
                'data',
                'icons',
                '{}.png'.format(name)
                )

        self.components.append(
            Label(
                pos=(0.03, y_positions[0]),
                height=text_height,
                text='Click on a tile to move there.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Floor'),
                pos=(0.95, y_positions[0]),
                height=image_height
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[1]),
                height=text_height,
                text='Click on monsters to attack them.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Goblin'),
                pos=(0.95, y_positions[1]),
                height=image_height
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[2]),
                height=text_height,
                text='Click on doors to open or close them.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Open door'),
                pos=(0.95, y_positions[2]),
                height=image_height
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[3]),
                height=text_height,
                text='Click on stairs to move between levels.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Upwards stairway'),
                pos=(0.95, y_positions[3]),
                height=image_height
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[4]),
                height=text_height,
                text='Press space to wait.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Hero'),
                pos=(0.95, y_positions[4]),
                height=image_height
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[5]),
                height=text_height,
                text='Kill monsters to level up.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.03, y_positions[6]),
                height=text_height,
                text='Harder monsters appear on lower floors.',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Image(
                filename=icon('Dragon'),
                pos=(0.95, y_positions[6]),
                height=image_height
                )
            )

    def step(self, ms_per_step: float, config: Config):
        """Update this state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.back_button.pressed:
            return MainMenu()

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

class HighScores:
    """The state that shows the high scores from the scores file.

    A list of high scores is shown that is loaded from the scores file.
    If the scores file does not exist, no scores are shown.
    """

    def __init__(self) -> None:
        """Initialise this state."""

        self.back_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Back'
            )

        self.components = [self.back_button]

        self.components.append(
            Label(
                pos=(0.5, 0.1),
                height=0.15,
                text='High Scores',
                font_type='serif',
                alignment='centre',
                colour=(255, 255, 255)
                )
            )

        y_positions = list(xrange(0.35, 1, 0.2))

        for i in range(3):
            self.components.append(
                Label(
                    pos=(0.3, y_positions[i]),
                    height=0.15,
                    text=str(i + 1),
                    font_type='sans',
                    alignment='centre',
                    colour=(255, 255, 255)
                    )
                )

        scores = load_scores()

        for i in range(len(scores)):
            self.components.append(
                ScoreDisplay(
                    pos=(0.4, y_positions[i]),
                    height=0.15,
                    score=scores[i]
                    )
                )

    def step(self, ms_per_step: float, config: Config):
        """Update this state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.back_button.pressed:
            return MainMenu()

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

class Options:
    """
    The state that shows the configuration of the program and allows
    the user to change it.

    Controls to change the fullscreen, resolution and volume settings
    are shown. The user must click the apply button to apply any
    changes they make.
    """

    def __init__(self) -> None:
        """Initialise this state."""

        self.config = None

        self.back_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Back'
            )

        y_positions = list(xrange(0.3, 1, 0.2))

        self.fullscreen_button = Button(
            pos=(0.7, y_positions[0]),
            width=0.25,
            height=0.08,
            text=''
            )

        self.res_display = ResolutionDisplay(
            pos=(0.7, y_positions[1]),
            height=0.08
            )

        self.vol_display = VolumeDisplay(
            pos=(0.7, y_positions[2]),
            height=0.08
            )

        self.apply_button = Button(
            pos=(0.5, y_positions[3]),
            width=0.16,
            height=0.08,
            text='Apply'
            )

        self.components = [
            self.back_button,
            self.fullscreen_button,
            self.res_display,
            self.vol_display,
            self.apply_button
            ]

        self.components.append(
            Label(
                pos=(0.5, 0.1),
                height=0.15,
                text='Options',
                font_type='serif',
                alignment='centre',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.05, y_positions[0]),
                height=0.08,
                text='Fullscreen',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.05, y_positions[1]),
                height=0.08,
                text='Resolution',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

        self.components.append(
            Label(
                pos=(0.05, y_positions[2]),
                height=0.08,
                text='Volume',
                font_type='sans',
                alignment='left',
                colour=(255, 255, 255)
                )
            )

    def step(self, ms_per_step: float, config: Config):
        """Update this state."""
        validate(self.step, locals())

        # Each state class is responsible for passing any queued events
        # to its components and updating its components.

        if self.config is None:
            self.config = config

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        # If the apply button has been pressed, the config must be
        # changed immediately.

        if self.back_button.pressed:
            return MainMenu()

        elif self.apply_button.pressed:
            return lambda: Options(), self.config

        # Each control must be updated using `self.config`. The values
        # they return are what should be stored in `self.config`.

        if self.fullscreen_button.pressed:

            self.config = self.config._replace(
                fullscreen=not self.config.fullscreen)

        self.fullscreen_button.text = \
            'Enabled' if self.config.fullscreen else 'Disabled'

        self.config = self.config._replace(
            resolution=self.res_display.res_update(self.config.resolution))

        self.config = self.config._replace(
            volume=self.vol_display.vol_update(self.config.volume))

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        # Before rendering each component, the screen must be cleared
        # to black.

        surface.fill((0, 0, 0))

        for c in self.components:
            c.render(surface)

def load_scores() -> list:
    """Returns the list of `Score` objects from the score file.

    Returns an empty list if the score file does not exist.
    """

    if os.path.exists(scores_path):
        with open(scores_path, 'rb') as file:
            return pickle.load(file)

    else:
        return []
