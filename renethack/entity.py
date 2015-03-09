import random

import renethack
from renethack.entity_types import Hero, Monster, Direction, Node
from renethack.world_types import World, Level
from renethack.util import validate, iter_to_maybe

NORTH = Direction()
NORTHEAST = Direction()
EAST = Direction()
SOUTHEAST = Direction()
SOUTH = Direction()
SOUTHWEST = Direction()
WEST = Direction()
NORTHWEST = Direction()

def direction_to_point(direction: Direction) -> tuple:
    """Convert a `Direction` to a vector."""
    validate(direction_to_point, locals())

    if direction is NORTH:
        return (0, 1)

    elif direction is NORTHEAST:
        return (1, 1)

    elif direction is EAST:
        return (1, 0)

    elif direction is SOUTHEAST:
        return (1, -1)

    elif direction is SOUTH:
        return (0, -1)

    elif direction is SOUTHWEST:
        return (-1, -1)

    elif direction is WEST:
        return (-1, 0)

    else:
        return (-1, 1)

def point_to_direction(point: tuple) -> Direction:
    """Convert a vector to a `Direction`."""
    validate(point_to_direction, locals())

    if point == (0, 1):
        return NORTH

    elif point == (1, 1):
        return NORTHEAST

    elif point == (1, 0):
        return EAST

    elif point == (1, -1):
        return SOUTHEAST

    elif point == (0, -1):
        return SOUTH

    elif point == (-1, -1):
        return SOUTHWEST

    elif point == (-1, 0):
        return WEST

    elif point == (-1, 1):
        return NORTHWEST

    else:
        raise ValueError('point {} has incorrect form'.format(point))

def find_path(point: tuple, target_point: tuple, level: Level) -> list:
    """Find a path from `point` to `target_point` through `level`."""
    validate(find_path, locals())

    open_list = [Node(None, point, target_point)]
    closed_list = []

    while True:

        # Get the node with the lowest final cost:
        open_list.sort(key=lambda n: n.final_cost)
        current_node = open_list[0]

        # Move the node to the closed list:
        open_list.remove(current_node)
        closed_list.append(current_node)

        if current_node.point == target_point:
            # If the current node is at the target point,
            # the path has been found.
            break

        x, y = current_node.point

        adjacent = [
            (x, y+1),
            (x+1, y+1),
            (x+1, y),
            (x+1, y-1),
            (x, y-1),
            (x-1, y-1),
            (x-1, y),
            (x-1, y+1)
            ]
        # The list of all adjacent points.

        for adj_point in adjacent:

            on_closed_list = any(
                n.point == adj_point
                for n in closed_list
                )

            adj_x, adj_y = adj_point
            tile = level.tiles[adj_x][adj_y]

            if ((tile.type.passable or tile.type is CLOSED_DOOR)
                    and not on_closed_list):

                open_node = iter_to_maybe(
                    n for n in open_list
                    if n.point == adj_point
                    )

                adj_node = Node(current_node, adj_point, target_point)

                if open_node is None:
                    open_list.append(adj_node)

                elif adj_node.cost < open_node.cost:
                    open_list.remove(open_node)
                    open_list.append(adj_node)

    path = []

    while current_node.point != point:

        current_x, current_y = current_node.point
        parent_x, parent_y = current_node.parent.point
        diff = (current_x - parent_x, current_y - parent_y)

        path.insert(0, point_to_direction(diff))

        current_node = current_node.parent

    return path

def rand_hero(name: str) -> Hero:
    """Return a randomly created hero."""
    validate(rand_hero, locals())

    return Hero(
        name=name,
        hit_points=random.randint(7, 10),
        defence=random.randint(0, 1),
        speed=random.randint(50, 75),
        strength=random.randint(1, 2)
        )

def new_goblin() -> Monster:
    """Returns a new goblin."""
    return Monster(
        name='Goblin',
        hit_points=3,
        defence=0,
        speed=50,
        strength=2,
        open_doors=True
        )

def new_giant_ant() -> Monster:
    """Returns a new giant ant."""
    return Monster(
        name='Giant Ant',
        hit_points=2,
        defence=0,
        speed=80,
        strength=1,
        open_doors=False
        )

def new_giant_rat() -> Monster:
    """Returns a new giant rat."""
    return Monster(
        name='Giant Rat',
        hit_points=1,
        defence=0,
        speed=80,
        strength=1,
        open_doors=False
        )

def new_gremlin() -> Monster:
    """Returns a new gremlin."""
    return Monster(
        name='Gremlin',
        hit_points=2,
        defence=0,
        speed=90,
        strength=1,
        open_doors=True
        )

def new_wolf() -> Monster:
    """Returns a new wolf."""
    return Monster(
        name='Wolf',
        hit_points=3,
        defence=0,
        speed=90,
        strength=3,
        open_doors=False
        )

def new_black_naga() -> Monster:
    """Returns a new black naga."""
    return Monster(
        name='Black Naga',
        hit_points=5,
        defence=3,
        speed=60,
        strength=4,
        open_doors=True
        )

def new_floating_eye() -> Monster:
    """Returns a new floating eye."""
    return Monster(
        name='Floating Eye',
        hit_points=3,
        defence=2,
        speed=60,
        strength=2,
        open_doors=False
        )

def new_gelationous_cube() -> Monster:
    """Returns a new gelationous cube."""
    return Monster(
        name='Gelationous Cube',
        hit_points=5,
        defence=2,
        speed=35,
        strength=4,
        open_doors=False
        )

def new_fire_elemental() -> Monster:
    """Returns a new fire elemental."""
    return Monster(
        name='Fire Elemental',
        hit_points=6,
        defence=2,
        speed=75,
        strength=5,
        open_doors=True
        )

def new_jabberwock() -> Monster:
    """Returns a new jabberwock."""
    return Monster(
        name='Jabberwock',
        hit_points=9,
        defence=3,
        speed=100,
        strength=6,
        open_doors=True
        )

def new_mind_flayer() -> Monster:
    """Returns a new mind flayer."""
    return Monster(
        name='Mind Flayer',
        hit_points=15,
        defence=5,
        speed=100,
        strength=8,
        open_doors=True
        )

def new_dragon() -> Monster:
    """Returns a new dragon."""
    return Monster(
        name='Dragon',
        hit_points=20,
        defence=5,
        speed=70,
        strength=6,
        open_doors=True
        )

def new_couatl() -> Monster:
    """Returns a new couatl."""
    return Monster(
        name='Couatl',
        hit_points=30,
        defence=10,
        speed=100,
        strength=10,
        open_doors=True
        )

monster_fns = [
    [new_giant_ant, new_gremlin, new_giant_rat],
    [new_giant_ant, new_gremlin, new_goblin, new_floating_eye, new_giant_rat],
    [new_giant_ant, new_gremlin, new_goblin, new_wolf, new_floating_eye],
    [new_goblin, new_wolf, new_floating_eye],
    [new_goblin, new_wolf, new_black_naga],
    [new_gelationous_cube, new_fire_elemental, new_black_naga],
    [new_gelationous_cube, new_fire_elemental, new_black_naga],
    [new_gelationous_cube, new_fire_elemental, new_jabberwock],
    [new_dragon, new_mind_flayer, new_jabberwock],
    [new_dragon, new_mind_flayer, new_couatl],
    ]

from renethack.world import UP_STAIRS, DOWN_STAIRS, CLOSED_DOOR, OPEN_DOOR
