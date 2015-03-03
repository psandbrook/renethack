import os
import pickle

import pygame
from pygame import Surface

import renethack
from renethack.gui import Label, Button, TextBox, WorldDisplay, StatusDisplay, MessageDisplay, ScoreDisplay
from renethack.entity_types import Hero, Score
from renethack.util import validate, xrange, get_maindir

LEVELS = 10
LEVEL_LENGTH = 30

scores_path = os.path.join(get_maindir(), 'scores.dat')

class MainMenu:

    def __init__(self) -> None:
        """Initialise the main menu to the default state."""

        button_y_pos = xrange(0.28, 1, 0.16)

        self.newgame_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.1,
            text='New Game'
            )

        self.instructions_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.1,
            text='How To Play'
            )

        self.scores_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.1,
            text='High Scores'
            )

        self.options_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.1,
            text='Options'
            )

        self.exit_button = Button(
            pos=(0.5, next(button_y_pos)),
            width=0.4,
            height=0.1,
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
                alignment='centre'
                )
            )

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

        elif self.newgame_button.pressed:
            return NewGame()

        elif self.instructions_button.pressed:
            return HowToPlay()

        elif self.scores_button.pressed:
            return HighScores()

        elif self.options_button.pressed:
            return Options()

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

class NewGame:

    def __init__(self) -> None:
        """Initialise this state."""
        validate(self.__init__, locals())

        self.text_box = TextBox(pos=(0.5, 0.5), height=0.1)
        self.components = [self.text_box]

        self.components.append(
            Label(
                pos=(0.5, 0.2),
                height=0.1,
                text='Enter name:',
                font_type='serif',
                alignment='centre'
                )
            )

    def step(self, ms_per_step: float):
        """Update this state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return MainGame(self.text_box.get_text())

                elif event.key == pygame.K_ESCAPE:
                    return MainMenu()

            for c in self.components:
                c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)

class MainGame:

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

    def step(self, ms_per_step: float):
        """Step the game state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.hero.wait()

            else:

                for c in self.components:
                    # Pass on event to each component.
                    c.check_event(event)

        for c in self.components:
            # Update each component.
            c.step(ms_per_step)

        if self.exit_button.pressed:

            if not self.score_saved:
                self.save_score()

            return MainMenu()

        for msg in self.hero.collect_messages():
            self.message_display.add_message(msg)

        if self.hero.hit_points > 0:

            # Check if a tile has been clicked.
            if self.world_display.pressed is not None:
                self.hero.path_to(self.world, self.world_display.pressed)

            if self.hero.energy < 100 or len(self.hero.actions) > 0:
                # Update the world if not waiting for input.
                renethack.world.step(self.world)

        elif not self.score_saved:
            # The player character has died.
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

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)

class HowToPlay:

    def __init__(self) -> None:
        """Initialise this state."""

        self.components = []

    def step(self, ms_per_step: float):
        """Update this state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)

class HighScores:

    def __init__(self) -> None:
        """Initialise this state."""

        self.exit_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Exit'
            )

        self.components = [self.exit_button]
        number_y_pos = list(xrange(0.35, 1, 0.2))

        self.components.append(
            Label(
                pos=(0.5, 0.1),
                height=0.15,
                text='High Scores',
                font_type='serif',
                alignment='centre'
                )
            )

        self.components.append(
            Label(
                pos=(0.3, number_y_pos[0]),
                height=0.15,
                text='1',
                font_type='sans',
                alignment='centre'
                )
            )

        self.components.append(
            Label(
                pos=(0.3, number_y_pos[1]),
                height=0.15,
                text='2',
                font_type='sans',
                alignment='centre'
                )
            )

        self.components.append(
            Label(
                pos=(0.3, number_y_pos[2]),
                height=0.15,
                text='3',
                font_type='sans',
                alignment='centre'
                )
            )

        scores = load_scores()

        for i in range(len(scores)):
            self.components.append(
                ScoreDisplay(
                    pos=(0.4, number_y_pos[i]),
                    height=0.15,
                    score=scores[i]
                    )
                )

    def step(self, ms_per_step: float):
        """Update this state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.exit_button.pressed:
            return MainMenu()

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)

class Options:

    def __init__(self) -> None:
        """Initialise this state."""

        self.title_label = Label(
            pos=(0.5, 0.1),
            height=0.15,
            text='Options',
            font_type='serif',
            alignment='centre'
            )

        self.exit_button = Button(
            pos=(0.1, 0.1),
            width=0.16,
            height=0.08,
            text='Exit'
            )

        self.components = [
            self.title_label,
            self.exit_button
            ]

    def step(self, ms_per_step: float):
        """Update this state."""
        validate(self.step, locals())

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            else:

                for c in self.components:
                    c.check_event(event)

        for c in self.components:
            c.step(ms_per_step)

        if self.exit_button.pressed:
            return MainMenu()

        return self

    def render(self, surface: Surface) -> None:
        """Render this state to the given surface."""
        validate(self.render, locals())

        surface.fill((0, 0, 0))
        for c in self.components:
            c.render(surface)

def load_scores() -> list:

    if os.path.exists(scores_path):
        with open(scores_path, 'rb') as file:
            return pickle.load(file)

    else:
        return []
