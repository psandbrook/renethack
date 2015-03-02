import random

import renethack
from renethack.entity_types import Hero, Monster
from renethack.world_types import World
from renethack.util import validate

def rand_hero(name: str) -> Hero:
    """Return a randomly created hero."""
    validate(rand_hero, locals())

    return Hero(
        name=name,
        hit_points=random.randint(7, 10),
        defence=random.randint(0, 1),
        speed=random.randint(50, 75),
        strength=random.randint(1, 3)
        )

def new_goblin(world: World) -> Monster:
    """Return a new goblin."""
    validate(new_goblin, locals())

    return Monster(
        name='Goblin',
        hit_points=3,
        defence=0,
        speed=50,
        strength=2,
        open_doors=True
        )

monster_fns = [
    [new_goblin],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    ]
