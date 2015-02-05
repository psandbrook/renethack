from pygame.event import EventType

from renethack.world_types import Level
from renethack.util import validate

class Monster:

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int) -> None:

        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength

        self.energy = 0

    # point: (int, int)
    def step(self, point: tuple, level: Level) -> None:
        """Update this entity.

        May modify values within `level`.
        """
        validate(self.step, locals())

class Hero:

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int) -> None:

        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength

        self.energy = 0
        self.actions = []

    # EventType -> None
    def check_event(self, event: EventType) -> None:
        """Check `event` with this entity."""
        validate(self.check_event, locals())

    # point: (int, int)
    # world: ([Level], Level, [Level])
    # return: ([Level], Level, [Level])
    def step(self, point: tuple, world: tuple) -> tuple:
        """Update this entity.

        May modify values within `world` or return a different world.
        """
        validate(self.step, locals())

        return world
