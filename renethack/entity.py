import random

from pygame.event import EventType

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
    # world: ([Level], Level, [Level])
    def step(self, point: tuple, world: tuple) -> None:
        """Update this entity.

        May modify values within `world`.
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

def rand_hero(name: str) -> Hero:
    """Return a randomly created hero."""
    validate(rand_hero, locals())

    return Hero(
        name=name,
        hit_points=random.randint(7, 10),
        defence=random.randint(0, 2),
        speed=random.randint(50, 75),
        strength=random.randint(1, 3)
        )

goblin = Monster(
    name='Goblin',
    hit_points=3,
    defence=0,
    speed=50,
    strength=2
    )

monsters = [goblin]
