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
        dir_x, dir_y = renethack.entity.direction_to_point(self.direction)
        target_x = hero_x + dir_x
        target_y = hero_y + dir_y

        hero = world.current_level.tiles[hero_x][hero_y].entity
        target_tile = world.current_level.tiles[target_x][target_y]

        hero.energy -= 100

        if target_tile.entity is not None:

            # Attack

            damage = min_clamp(hero.strength - target_tile.entity.defence, 0)
            target_tile.entity.hit_points -= damage

            hero.add_message('You hit the {} for {} damage!'.format(
                target_tile.entity.name, damage))

            hero.actions = []

        else:

            if target_tile.type is CLOSED_DOOR:
                hero.add_message('You open the door.')
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
        dir_x, dir_y = renethack.entity.direction_to_point(self.direction)
        target_x = hero_x + dir_x
        target_y = hero_y + dir_y

        hero = world.current_level.tiles[hero_x][hero_y].entity
        target_tile = world.current_level.tiles[target_x][target_y]

        level_length = len(world.current_level.tiles)
        centre = (level_length - 1) // 2

        hero.energy -= 100

        if target_tile.entity is not None:

            # Attack

            damage = min_clamp(hero.strength - target_tile.entity.defence, 0)
            target_tile.entity.hit_points -= damage

            hero.add_message('You hit the {} for {} damage!'.format(
                target_tile.entity.name, damage))

        elif target_tile.type is UP_STAIRS:

            # Go to upper level
            renethack.world.remove_entity(world.current_level, world.hero)

            world.lower_levels.insert(0, world.current_level)
            world.current_level = world.upper_levels[0]
            world.upper_levels = world.upper_levels[1:]

            down_stairs = renethack.world.get_tiles(
                world.current_level, DOWN_STAIRS)

            world.hero = down_stairs[0]
            renethack.world.remove_entity(world.current_level, world.hero)
            renethack.world.add_entity(world.current_level, world.hero, hero)

            hero.add_message('You ascend the stairs.')

        elif target_tile.type is DOWN_STAIRS:

            # Go to lower level
            renethack.world.remove_entity(world.current_level, world.hero)

            world.upper_levels.insert(0, world.current_level)
            world.current_level = world.lower_levels[0]
            world.lower_levels = world.lower_levels[1:]

            world.hero = (centre, centre)
            renethack.world.remove_entity(world.current_level, world.hero)
            renethack.world.add_entity(world.current_level, world.hero, hero)

            hero.add_message('You descend the stairs.')

        elif target_tile.type is OPEN_DOOR:
            target_tile.type = CLOSED_DOOR
            hero.add_message('You close the door.')

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

        hero_x, hero_y = world.hero
        hero = world.current_level.tiles[hero_x][hero_y].entity

        if self.hit_points <= 0:

            renethack.world.remove_entity(world.current_level, point)

            hero.experience += 1
            hero.score += 10
            hero.add_message('The {} dies!'.format(self.name))

            return

        if self.energy >= 100:

            # Calculate adjacent tile that is closest to hero and move
            # there.

            path = renethack.entity.find_path(
                point, world.hero, world.current_level)

            current_x, current_y = point
            dir_x, dir_y = renethack.entity.direction_to_point(path[0])
            target_x = current_x + dir_x
            target_y = current_y + dir_y

            target_tile = world.current_level.tiles[target_x][target_y]

            if ((not target_tile.type.passable
                        and (target_tile.type is not CLOSED_DOOR
                            or not self.open_doors))
                    or (target_tile.entity is not None
                        and target_tile.entity is not hero)):

                # If nothing can be done, return immediately.
                return

            self.energy -= 100

            if target_tile.entity is hero:

                # Attack hero

                damage = min_clamp(self.strength - hero.defence, 0)
                hero.hit_points -= damage

                hero.add_message('The {} hits you for {} damage!'.format(
                    self.name, damage))

                if hero.hit_points <= 0:

                    renethack.world.remove_entity(
                        world.current_level, world.hero)

                    hero.add_message('You have died.')

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

        self.level = 1
        self.experience = 0
        self.score = 0
        self.energy = 0
        self.hp_counter = 0
        self.actions = []
        self.messages = []
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
            self.add_message('You cannot move there.')
            return

        elif world.hero == point:
            self.wait()
            return

        directions = renethack.entity.find_path(
            world.hero, point, world.current_level)

        moves = [Move(d) for d in directions]

        if (tile.type is UP_STAIRS
                or tile.type is DOWN_STAIRS
                or tile.type is OPEN_DOOR):
            self.actions = moves[:-1]
            self.actions.append(Use(directions[-1]))

        else:
            self.actions = moves

    def wait(self) -> None:
        self.actions = [Wait()]

    def add_message(self, msg: str) -> None:
        validate(self.add_message, locals())
        self.messages.append(msg)

    def collect_messages(self) -> list:
        messages = self.messages
        self.messages = []
        return messages

    def step(self, point: tuple, world: World) -> None:
        """Update this entity.

        May modify values within `world`.
        """
        validate(self.step, locals())

        if self.experience >= 6:

            self.experience = 0
            self.level += 1
            self.score += 100
            self.add_message('Welcome to level {}.'.format(self.level))

            self.max_hit_points += 1
            self.defence += 1
            self.speed += 10
            self.strength += 1

        if self.hit_points < self.max_hit_points:

            if self.hp_counter >= 10:
                self.hp_counter = 0
                self.hit_points += 1

            else:
                self.hp_counter += 1

        else:
            self.hp_counter = 0

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

from renethack.world import UP_STAIRS, DOWN_STAIRS, CLOSED_DOOR, OPEN_DOOR
from renethack.entity import NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST, WEST, NORTHWEST
