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

from renethack.world import UP_STAIRS, DOWN_STAIRS, CLOSED_DOOR, OPEN_DOOR
