import collections
from types import GeneratorType

from pygame.event import EventType

import renethack
from renethack.world_types import World, Level
from renethack.util import validate, iter_to_maybe, min_clamp

class Direction:
    pass

class Move:
    """Move the hero in the saved direction."""

    def __init__(self, direction: Direction) -> None:
        validate(self.__init__, locals())

        self.direction = direction

    def execute(self, world: World) -> None:
        validate(self.execute, locals())

        hero_x, hero_y = world.hero
        dir_x, dir_y = direction_to_point(self.direction)
        target_x = hero_x + dir_x
        target_y = hero_y + dir_y

        hero = world.current_level.tiles[hero_x][hero_y].entity
        target_tile = world.current_level.tiles[target_x][target_y]

        hero.energy -= 100

        if target_tile.entity is not None:

            # Attack
            target_tile.entity.hit_points -= min_clamp(
                hero.strength - target_tile.entity.defence,
                0
                )

            hero.actions = []

        else:

            if target_tile.type is CLOSED_DOOR:
                target_tile.type = OPEN_DOOR

            # Move
            renethack.world.remove_entity(world.current_level, world.hero)

            renethack.world.add_entity(
                world.current_level,
                (target_x, target_y),
                hero
                )

            world.hero = (target_x, target_y)

class Use:
    """Use the object in the saved direction."""

    def __init__(self, direction: Direction) -> None:
        validate(self.__init__, locals())

        self.direction = direction

    def execute(self, world: World) -> None:
        validate(self.execute, locals())

        hero_x, hero_y = world.hero
        dir_x, dir_y = direction_to_point(self.direction)
        target_x = hero_x + dir_x
        target_y = hero_y + dir_y

        hero = world.current_level.tiles[hero_x][hero_y].entity
        target_tile = world.current_level.tiles[target_x][target_y]

        level_length = len(world.current_level.tiles)
        centre = (level_length - 1) // 2

        hero.energy -= 100

        if target_tile.entity is not None:

            # Attack
            target_tile.entity.hit_points -= min_clamp(
                hero.strength - target_tile.entity.defence,
                0
                )

            hero.actions = []

        elif target_tile.type is UP_STAIRS:

            # Go to upper level
            renethack.world.remove_entity(world.current_level, world.hero)

            world.lower_levels.insert(0, world.current_level)
            world.current_level = world.upper_levels[0]
            world.upper_levels = world.upper_levels[1:]

            world.hero = (centre, centre)
            renethack.world.remove_entity(world.current_level, world.hero)
            renethack.world.add_entity(world.current_level, world.hero, hero)

            hero.actions = []

        elif target_tile.type is DOWN_STAIRS:

            # Go to lower level
            renethack.world.remove_entity(world.current_level, world.hero)

            world.upper_levels.insert(0, world.current_level)
            world.current_level = world.lower_levels[0]
            world.lower_levels = world.lower_levels[1:]

            world.hero = (centre, centre)
            renethack.world.remove_entity(world.current_level, world.hero)
            renethack.world.add_entity(world.current_level, world.hero, hero)

            hero.actions = []

class Wait:
    """Do nothing. Does not cost energy."""

    def execute(self, world: World) -> None:
        validate(self.execute, locals())

class Monster:
    """The type of any entity that is not the player character."""

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int,
            open_doors: bool) -> None:
        """Initialise a new entity.

        name: display name
        hit_points: health
        defence: damage reduction
        speed: energy gain per turn
        strength: damage
        open_doors: ability to open doors
        """
        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength
        self.open_doors = open_doors

        self.energy = 0
        self.icon_name = name

    def step(self, point: tuple, world: World) -> None:
        """Update this entity.

        May modify values within `level`.
        """
        validate(self.step, locals())

        if self.hit_points <= 0:
            renethack.world.remove_entity(world.current_level, point)
            return

        if self.energy >= 100:

            # Calculate adjacent tile that is closest to hero and move
            # there.

            path = find_path(point, world.hero, world.current_level)

            current_x, current_y = point
            dir_x, dir_y = direction_to_point(path[0])
            target_x = current_x + dir_x
            target_y = current_y + dir_y

            target_tile = world.current_level.tiles[target_x][target_y]

            if ((not target_tile.type.passable
                        and (target_tile.type is not CLOSED_DOOR
                            or not self.open_doors))
                    or (target_tile.entity is not None
                        and (target_x, target_y) != world.hero)):
                return

            self.energy -= 100

            if (target_x, target_y) == world.hero:

                # Attack hero
                target_tile.entity.hit_points -= min_clamp(
                    self.strength - target_tile.entity.defence,
                    0
                    )

            else:

                if target_tile.type is CLOSED_DOOR:
                    target_tile.type = OPEN_DOOR

                # Move
                renethack.world.remove_entity(world.current_level, point)

                renethack.world.add_entity(
                    world.current_level,
                    (target_x, target_y),
                    self
                    )

        self.energy += self.speed

class Hero:
    """The type of the player character."""

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int) -> None:
        """Initialise a new entity.

        name: display name
        hit_points: health
        defence: damage reduction
        speed: energy gain per turn
        strength: damage
        open_doors: ability to open doors
        """
        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength

        self.energy = 0
        self.actions = []
        self.icon_name = 'Hero'

    def path_to(self, world: World, point: tuple) -> None:
        """
        Generate the necessary actions to
        move the hero to `point`.
        """
        validate(self.path_to, locals())

        x, y = point
        tile = world.current_level.tiles[x][y]

        if not tile.type.passable and tile.type is not CLOSED_DOOR:
            return

        elif world.hero == point:
            self.actions.append(Wait())
            return

        directions = find_path(world.hero, point, world.current_level)
        moves = [Move(d) for d in directions]

        if tile.type is UP_STAIRS or tile.type is DOWN_STAIRS:
            self.actions.extend(moves[:-1])
            self.actions.append(Use(directions[-1]))

        else:
            self.actions.extend(moves)

    def step(self, point: tuple, world: World) -> None:
        """Update this entity.

        May modify values within `world`.
        """
        validate(self.step, locals())

        if self.energy >= 100: 

            action = self.actions[0]
            self.actions = self.actions[1:]

            action.execute(world)

        self.energy += self.speed

class Node:
    """A point with extra metadata."""

    def __init__(
            self,
            parent,
            point: tuple,
            target_point: tuple) -> None:
        validate(self.__init__, locals())

        self.parent = parent
        self.point = point

        x, y = self.point
        target_x, target_y = target_point

        self.cost = 0 if parent is None else parent.cost + 1
        self.remaining_cost = abs(x - target_x) + abs(y - target_y)
        self.final_cost = self.cost + self.remaining_cost

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

from renethack.world import UP_STAIRS, DOWN_STAIRS, CLOSED_DOOR, OPEN_DOOR
